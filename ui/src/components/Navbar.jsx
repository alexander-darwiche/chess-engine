import React, { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import "../style/Navbar.css";


const Navbar = () => {
  
    const navigate = useNavigate();

  return (
    <nav>
      <Link to="/" className="title">
        Home
      </Link>
      <div>
        <span></span>
        <span></span>
        <span></span>
      </div>
      <ul>
            <li>
                <NavLink to="/">User</NavLink>
            </li>
            <li>
                <NavLink to="/">Admin</NavLink>
            </li>
      </ul>
    </nav>
  );
};

export default Navbar;
