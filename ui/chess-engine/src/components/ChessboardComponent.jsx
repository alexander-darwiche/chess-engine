import React, { useState } from 'react';
import {Chessboard} from 'react-chessboard';
import '../styling/ChessboardComponent.css'

const ChessboardComponent = () => {
  const [fen, setFen] = useState('start');

  // Function to change the position of the pieces
  const changePosition = () => {
    // Set the FEN string representing the new piece positions
    // Example: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    setFen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
  };

  return (
    <div className="chessboard">
      <h1>Chessboard with Custom Position</h1>
      {/* Pass the fen prop to set the initial position of the pieces */}
      <Chessboard fen={fen} />

      {/* Button to change the position of the pieces */}
      <button onClick={changePosition}>Change Position</button>
    </div>
  );
};

export default ChessboardComponent;
