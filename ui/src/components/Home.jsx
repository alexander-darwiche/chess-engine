import React, { useEffect, useState } from "react";
import "../style/Home.css";
import { Chessboard } from "react-chessboard";



const Home = () => {

  return (
    <div className="home-page">
      <div className="chess-container">
        <Chessboard id="BasicBoard" />
      </div>
    </div>
  );
};

export default Home;