# run this code with follwing command line args
# argv[1] -> bot1 path (absolute)
# argv[2] -> bot2 path (absolute)
# argv[3] -> log file path (absolute)
"""if __name__ == "__main__" and __package__ is None:
	__package__  = "." """

from subprocess import call, Popen, PIPE
from select import poll, POLLIN
from signal import signal, alarm, SIGALRM, SIGPIPE, SIG_DFL
from sys import exit, argv
from val_parser import parser_func, EndGameError

time_limits = {
    "cpp": 5000,
    "c": 2000,
    "py": 6000,
}


ext1 = argv[1]
ext2 = argv[2]

# print argv[3]

plist1 = ["prlimit", "-p", ""]
plist2 = ["prlimit", "-p", ""]

log_file = open('../matches/log' + argv[3], 'w')

# The following 2 lines are to compile the code.
# When the code is compiled, an a.out file is generated. But if 2 cpp files need to be compiled, the object file of the second will overwrite the first
# The -o option allows us to specify an alternate name.
# NOTE: Compiling will not be done in the BM code in the final project. This is only here for convenience
# call(["g++", "-o", "player1", "bot.cpp"])
# call(["g++", "-o", "player2", "bot.cpp"])
call(["g++", "-std=c++11", "-o", "val", "val.cpp"])

# The stdbuf command on the command line is used in order to set the buffering for the input, output and error streams resp for the succeeding command
# In this case, all the streams are unbuffered for the 2 processes

try:
    if ext1 == "cpp":
        plist1.extend(("--nofile=5", "--nproc=500", "--as=21460"))
        popen_obj1 = Popen(["stdbuf", "-o0", "-i0", "-e0",
                            "../bots/player1"], stdin=PIPE, stdout=PIPE)
    elif ext1 == "c":
        plist1.extend(("--nofile=5", "--nproc=500", "--as=21460"))
        popen_obj1 = Popen(["stdbuf", "-o0", "-i0", "-e0",
                            "../bots/player1"], stdin=PIPE, stdout=PIPE)
    else:
        plist1.extend(("--nofile=5", "--nproc=500", "--as=32740"))
        popen_obj1 = Popen(["stdbuf", "-o0", "-i0", "-e0",
                            "python", "../bots/player1"], stdin=PIPE, stdout=PIPE)
except Exception as e:
    print "Error occured in process creation"
    end_code(-1)

try:
    if ext2 == "cpp":
        plist2.extend(("--nofile=5", "--nproc=500", "--as=21460"))
        popen_obj2 = Popen(["stdbuf", "-o0", "-i0", "-e0",
                            "../bots/player2"], stdin=PIPE, stdout=PIPE)
    elif ext2 == "c":
        plist2.extend(("--nofile=5", "--nproc=500", "--as=21460"))
        popen_obj2 = Popen(["stdbuf", "-o0", "-i0", "-e0",
                            "../bots/player2"], stdin=PIPE, stdout=PIPE)
    else:
        plist2.extend(("--nofile=5", "--nproc=500", "--as=32740"))
        popen_obj2 = Popen(["stdbuf", "-o0", "-i0", "-e0",
                            "python", "../bots/player2"], stdin=PIPE, stdout=PIPE)
except Exception as e:
    print "Error occurred in process creation"
    end_code(-1)

popen_val_obj = Popen(["stdbuf", "-o0", "-i0", "-e0",
                       "./val"], stdin=PIPE, stdout=PIPE)

plist1[2] = str(popen_obj1.pid)
plist2[2] = str(popen_obj2.pid)
call(plist1)
call(plist2)

if argv[4] == "True":               # Swap the popen object
    swap_obj = popen_obj2
    popen_obj2 = popen_obj1
    popen_obj1 = swap_obj

# print "All processes successfully fired"
# The below objects are polling objects of the select module
# They can be used to listen to a particular stream and notify whenever an event takes place at that stream
poll_obj1 = poll()
poll_obj2 = poll()

# The below commands indicate the polling objects which streams to listen at and which event to listen for
# POLLIN is a constant defined in the select module. It represents input from the stream.
# So the first line means:
# poll_obj1 is listening at popen_obj1's output stream for any data to come out
# poll_obj2 is listening at popen_obj2's output stream for any data to come out
poll_obj1.register(popen_obj1.stdout.fileno(), POLLIN)
poll_obj2.register(popen_obj2.stdout.fileno(), POLLIN)

time_limit1 = time_limits[ext1]
time_limit2 = time_limits[ext2]

# This is a signal handler. It is a callback function. It is taken as a paramater to another function and is run there
# The first parameter is signal number, which is an integer to identify the signal
# The second is a special object, which holds some extra data about the cause of the signal
# This handler will be used ahead.


def handler(signum, frame):
    raise IOError("Unable to open device")


# The below function is used to link a handler with a SIGNAL. Meaning that when the signal occurs, the handler function is called
# SIGALRM is just like POLLIN. It is a constant defined in the signal module and is used to represent Signal Alarm.
# We use this signal alarm as an alarm clock while reading the input.
signal(SIGALRM, handler)

# This is the code for the end condition.
# Before the code terminates, this function needs to be run


def end_code(exit_code):
    #	print "Cleaning up processes"
    if popen_obj1.poll() is None:
        popen_obj1.kill()
    if popen_obj2.poll() is None:
        popen_obj2.kill()
    if popen_val_obj.poll() is None:
        popen_val_obj.kill()
#	print "Within BM" + str(exit_code)
    exit(exit_code)


# This poll is different from the above poll. This one is a method of the popen object
# It returns none is the process is alive and a -ve value if it is dead
# So the below line means: if both processes are alive:
try:
    if not popen_obj1.poll() and not popen_obj2.poll():
        popen_obj1.stdin.write("0\n")
        popen_obj2.stdin.write("1\n")
        # This poll method is again different. It belongs to the poll object
        # It represents the time which the poll object will wait to receive an input
        if popen_obj1.poll():
            log_file.write("i,0,Premature termination")
            end_code(102)
        if popen_obj2.poll():
            log_file.write("i,1,Premature termination")
            end_code(101)
        temp = poll_obj1.poll(time_limit1)
        if temp:  # If temp is not empty, meaning some event occurred
            # If the occurred event was a POLLIN. Ideally, no other event should occur
            if temp[0][1] is POLLIN:
                try:
                    # Like setting an alarm. The alarm will go off in 1 second
                    alarm(1)
                    p = popen_obj1.stdout.readline()  # Attempt to read the output. If it blocks, the alarm will go off in one second, and the handler will be called, which will raise an exception. The exception will be caught by the enclosing try-catch block
                    alarm(0)  # If read was successful, disable the alarm
                    intermediate_string = parser_func(p, popen_val_obj)
                    print(intermediate_string)
                    if intermediate_string[0] != -2:
                        print "in1"
                        log_file.write('v,0,' + intermediate_string[0])
                        print(intermediate_string)
                        popen_obj1.stdin.write(intermediate_string[0])
                    else:
                        if intermediate_string[3] == 0:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(102)
                        elif intermediate_string[3] == 1:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(101)
                        elif intermediate_string[3] == -1:
                            log_file.write(
                                'd,'+intermediate_string[1])
                            end_code(100)
                    #log_file.write('v,0,' + p)
                    # popen_obj2.stdin.write(intermediate_string)
                except EndGameError as end_ev:
                    log_file.write(str(end_ev))
                    end_code(end_ev.winner)
                except ValueError as v:
                    log_file.write('l,0,' + p.rstrip('\n') + ',' + str(v))
                    end_code(102)  # was 102
                except IOError as e:
                    # try:
                    intermediate_string = parser_func(p, popen_val_obj)
                    if intermediate_string[0] != -2:
                        print(intermediate_string)
                        log_file.write('v,0,' + intermediate_string[0])
                        popen_obj1.stdin.write(intermediate_string[0])
                    else:
                        if intermediate_string[3] == 0:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(102)
                        elif intermediate_string[3] == 1:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(101)
                        elif intermediate_string[3] == -1:
                            log_file.write(
                                'd,'+intermediate_string[1])
                            end_code(100)
                        #log_file.write('v,0,' + p)
                        # popen_obj2.stdin.write(intermediate_string)
                    #log_file.write('i,0' + str(e))
                    # end_code(102)
                    # except EndGameError as end_ev:
                    #    log_file.write(str(end_ev))
                    #    end_code(end_ev.winner)
            else:
                log_file.write('i,0,No I/O detected')
                end_code(102)
        else:
            log_file.write('i,0,No I/O detected')
            end_code(102)
    else:
        log_file.write('i,0,Premature termination')
        end_code(102)

    if not popen_obj1.poll() and not popen_obj2.poll():
        temp = poll_obj2.poll(time_limit2)
        if temp:
            if temp[0][1] is POLLIN:
                try:
                    alarm(1)
                    p = popen_obj2.stdout.readline()
                    alarm(0)
                    intermediate_string = parser_func(p, popen_val_obj)
                    if intermediate_string[0] != 2:
                        log_file.write('v,1,' + intermediate_string[0])
                        popen_obj1.stdin.write(intermediate_string[0])
                    else:
                        if intermediate_string[3] == 0:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(102)
                        elif intermediate_string[3] == 1:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(101)
                        elif intermediate_string[3] == -1:
                            log_file.write(
                                'd,'+intermediate_string[1])
                            end_code(100)
                except EndGameError as end_ev:
                    log_file.write(str(end_ev))
                    end_code(end_ev.winner)
                except ValueError as v:
                    log_file.write(
                        'l,1,' + intermediate_string.rstrip('\n') + ',' + str(v))  # was 2
                    end_code(101)
                except IOError as e:
                    # try:
                    intermediate_string = parser_func(p, popen_val_obj)
                    if intermediate_string[0] != -2:
                        log_file.write('v,1,' + intermediate_string[0])
                        popen_obj1.stdin.write(intermediate_string[0])
                    else:
                        if intermediate_string[3] == 0:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(102)
                        elif intermediate_string[3] == 1:
                            log_file.write(
                                'w,'+intermediate_string[1], ','+intermediate_string[2])
                            end_code(101)
                        elif intermediate_string[3] == -1:
                            log_file.write(
                                'd,'+intermediate_string[1])
                            end_code(100)
                    """
                        log_file.write('v,1,' + intermediate_string)
                        popen_obj1.stdin.write(intermediate_string)
                    except EndGameError as end_ev:
                        log_file.write(str(end_ev))
                        end_code(end_ev.winner)
                    #log_file.write('i,1,' + str(e))
                    # end_code(101)
                    """
            else:
                log_file.write('i,1,No I/O detected')
                end_code(101)
        else:
            log_file.write('i,1,No I/O detected')
            end_code(101)
    else:
        log_file.write('i,1,Premature termination')
        end_code(101)

    # The below code is for the while(1) implementation. Used a for loop to run a max of 50 iterations
    while(1):
        if not popen_obj1.poll() and not popen_obj2.poll():
            temp = poll_obj1.poll(time_limit1)
            if temp:
                if temp[0][1] is POLLIN:
                    try:
                        alarm(1)
                        p = popen_obj1.stdout.readline()
                        alarm(0)
                        intermediate_string = parser_func(p, popen_val_obj)
                        if intermediate_string[0] != -2:
                            log_file.write('v,0,' + intermediate_string[0])
                            popen_obj1.stdin.write(intermediate_string[0])
                        else:
                            if intermediate_string[3] == 0:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(102)
                            elif intermediate_string[3] == 1:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(101)
                            elif intermediate_string[3] == -1:
                                log_file.write(
                                    'd,'+intermediate_string[1])
                                end_code(100)
                        #log_file.write('v,0,' + p)
                        # popen_obj2.stdin.write(intermediate_string)
                    except EndGameError as end_ev:
                        log_file.write(str(end_ev))
                        end_code(end_ev.winner)
                    except ValueError as v:
                        log_file.write('l,0,' + p.rstrip('\n') + ',' + str(v))
                        end_code(102)  # was 102
                    except IOError as e:
                        # try:
                        intermediate_string = parser_func(p, popen_val_obj)
                        print(intermediate_string)
                        if intermediate_string[0] != -2:
                            log_file.write('v,0,' + intermediate_string[0])
                            popen_obj1.stdin.write(intermediate_string[0])
                        else:
                            if intermediate_string[3] == 0:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(102)
                            elif intermediate_string[3] == 1:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(101)
                            elif intermediate_string[3] == -1:
                                log_file.write(
                                    'd,'+intermediate_string[1])
                                end_code(100)
                            #log_file.write('v,0,' + p)
                            # popen_obj2.stdin.write(intermediate_string)
                        #log_file.write('i,0' + str(e))
                        # end_code(102)
                        # except EndGameError as end_ev:
                        #    log_file.write(str(end_ev))
                        #    end_code(end_ev.winner)
                else:
                    log_file.write('i,0,No I/O detected')
                    end_code(102)
            else:
                log_file.write('i,0,No I/O detected')
                end_code(102)
        else:
            log_file.write('i,0,Premature termination')
            end_code(102)

        if not popen_obj1.poll() and not popen_obj2.poll():
            temp = poll_obj2.poll(time_limit2)
            if temp:
                if temp[0][1] is POLLIN:
                    try:
                        alarm(1)
                        p = popen_obj2.stdout.readline()
                        alarm(0)
                        intermediate_string = parser_func(p, popen_val_obj)
                        if intermediate_string[0] != -2:
                            log_file.write('v,1,' + intermediate_string[0])
                            popen_obj1.stdin.write(intermediate_string[0])
                        else:
                            if intermediate_string[3] == 0:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(102)
                            elif intermediate_string[3] == 1:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(101)
                            elif intermediate_string[3] == -1:
                                log_file.write(
                                    'd,'+intermediate_string[1])
                                end_code(100)
                        # log_file.write('v,1,' + intermediate_string)  # was 2
                        # popen_obj1.stdin.write(intermediate_string)
                    except EndGameError as end_ev:
                        log_file.write(str(end_ev))
                        end_code(end_ev.winner)
                    except ValueError as v:
                        log_file.write(
                            'l,1,' + intermediate_string.rstrip('\n') + ',' + str(v))
                        end_code(101)
                    except IOError as e:
                        # try:
                        intermediate_string = parser_func(p, popen_val_obj)
                        if intermediate_string[0] != -2:
                            log_file.write('v,1,' + intermediate_string[0])
                            popen_obj1.stdin.write(intermediate_string[0])
                        else:
                            if intermediate_string[3] == 0:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(102)
                            elif intermediate_string[3] == 1:
                                log_file.write(
                                    'w,'+intermediate_string[1], ','+intermediate_string[2])
                                end_code(101)
                            elif intermediate_string[3] == -1:
                                log_file.write(
                                    'd,'+intermediate_string[1])
                                end_code(100)
                            #log_file.write('v,1,' + intermediate_string)
                            # popen_obj1.stdin.write(intermediate_string)
                        #log_file.write('i,1,' + str(e))
                        # end_code(101)
                        # except EndGameError as end_ev:
                            # log_file.write(str(end_ev))
                            # end_code(end_ev.winner)
                else:
                    log_file.write('i,1,No I/O detected')
                    end_code(101)
            else:
                log_file.write('i,1,No I/O detected')
                end_code(101)
        else:
            log_file.write('i,1,Premature termination')
            end_code(101)
    else:
        log_file.write('i,1,Match did not terminate')
        end_code(100)  # was 100
except Exception as e:
    log_file.write(str(e))
    end_code(255)
end_code()
