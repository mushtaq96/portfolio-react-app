import About from "./components/About";
import Contact from "./components/Contact";
import Home from "./components/Home";
import Navbar from "./components/Navbar";
import Skills from "./components/Skills";
import Work from "./components/Work";


function App() {
  return (
    <div className="App">
      <Navbar />
      <div className="sm:pt-20 md:pt-0 lg:pt-0">
        <Home />
        <About />
        <Skills />
        <Work />
        <Contact />
      </div>
    </div >
  );
}

export default App;
