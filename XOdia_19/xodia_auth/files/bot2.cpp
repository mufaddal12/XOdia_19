#include <iostream>
#include <string>
#include <vector>
#include <chrono>

using namespace std;

//white = 0, black = 1

class Board{
    vector<vector<int>> board;
    int whites, blacks;

public:
    Board();
    int getWhites();
    int getBlacks();
    void apply(int move[]);
    void revert(int move[]);
    void display();
};

Board::Board(){
    board = {
				    {  0,  0,  0,  0},

				  {  0,  0,  0,  0,  0},

			    { -1, -1,  0,  0, -1, -1},

			  { -1, -1, -1, -1, -1, -1, -1},

				 { -1, -1,  1,  1, -1, -1},

				   {  1,  1,  1,  1,  1},

					 {  1,  1,  1,  1}
			 };

    whites = 11;
    blacks = 11;
}

int Board::getWhites(){
    return whites;
}

int Board::getBlacks(){
    return blacks;
}

//0,1 indices as first piece, 2,3 indices as second piece
void Board::apply(int move[]){
    int whoseMove;
    if(board[move[0]][move[1]] == 0)
        whoseMove = 0;
    else
        whoseMove = 1;

    //SE-NW
    if(abs(move[0] - move[2]) == 1 && abs(move[1] - move[3]) == 1){
        if(move[0] < move[2]){
            board[move[0]][move[1]] = -1;
            board[move[2] + 1][move[3] + 1] = whoseMove;
        }else{
            board[move[0]][move[1]] = -1;
            board[move[2] -1][move[3] -1] = whoseMove;
        }
    }

    //SW-NE
    else if(move[1] == move[3]){
        if(move[0] < move[2]){
            board[move[0]][move[1]] = -1;
            board[move[2] + 1][move[3]] = whoseMove;
        }else{
            board[move[0]][move[1]] = -1;
            board[move[2] - 1][move[3]] = whoseMove;
        }
    }

    //E-W
    else if(move[0] == move[2]){
        if(move[1] < move[3]){
            board[move[0]][move[1]] = -1;
            board[move[2]][move[3] + 1] = whoseMove;
        }else{
            board[move[0]][move[1]] = -1;
            board[move[2]][move[3] - 1] = whoseMove;
        }
    }
}

void Board::display(){
	char row = 'A';
	int dia = 7;
	for (int i = 0; i < 4; i++){
		for (int j = 2 - i; j >= 0; j--){
			cout << " ";
		}
		cout << row << " ";
		for (int j = 0; j < board[i].size(); j++){
			if (board[i][j] == -1) cout << "+ ";
			else if (board[i][j] == 0) cout << "O ";
			else cout << "@ ";
		}
		cout << endl;
		row++;
	}
	for (int i = 4; i < 7; i++){
		for (int j = 0; j < i - 3; j++){
			cout << " ";
		}
		cout << row << " ";
		for (int j = 0; j < board[i].size(); j++){
			if (board[i][j] == -1) cout << "+ ";
			else if (board[i][j] == 0) cout << "O ";
			else cout << "@ ";
		}
		cout << dia << endl;
		row++;
		dia--;
	}
	for (int i = 0; i < 6; i++) cout << " ";
	for (int i = 0; i < 4; i++, dia--) cout << 5 - dia << " ";
	cout << endl;
}

int main(){
    Board board;
    board.display();
    int temp[4] = {5,1,4,2};
    board.apply(temp);
    board.display();

    return 0;
}
