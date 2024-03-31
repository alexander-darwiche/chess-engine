import { render } from 'react-dom';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./components/Home";
import Navbar from "./components/Navbar";

function App() {

  return (
    <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
    </BrowserRouter>
  )
}

const rootElement = document.getElementById("root")
render(<App />, rootElement)

