import React, {useState} from 'react'
import Logo from '../assets/logo1.png'
import {FaBars, FaTimes, FaGithub, FaLinkedin} from 'react-icons/fa'
import { HiOutlineMail } from 'react-icons/hi'
import {BsFillPersonLinesFill} from 'react-icons/bs'
import {Link} from 'react-scroll'

const Navbar = () =>{
    const [nav, setNav] = useState(false)
    const handleClick = () => setNav(!nav)

    return(
        <div className='fixed w-full h-[80px] flex justify-between items-center px-4 bg-[#0a192f] text-gray-300'>
            <div className='cursor-pointer'>   
                <Link to="home" smooth={true} duration={500}>
                    <img src={Logo} alt="Logo" style={{width:'50px', borderRadius: '10px'}}/>
                </Link>
            </div>

            {/* menuu */}
     
            <ul className='hidden md:flex'>
                <li className='hover:text-red-500'>
                    <Link to="home" smooth={true} duration={500}>
                        Home
                    </Link>
                </li>
                <li className='hover:text-red-500'>
                    <Link to="about" smooth={true} duration={500}>
                        About
                    </Link>
                </li>
                <li className='hover:text-red-500'>
                    <Link to="skills" smooth={true} duration={500}>
                        Skills
                    </Link>
                </li>
                <li className='hover:text-red-500'>
                    <Link to="work" smooth={true} duration={500}>
                        Work
                    </Link>
                </li>
                <li className='hover:text-red-500'>
                    <Link to='contact' smooth={true} duration={500}>
                        Contact
                    </Link>
                </li>
            </ul>
          

            {/* hamburger */}
            <div className='md:hidden z-10' onClick={handleClick}>
                {!nav ? <FaBars/> : <FaTimes/>}
            </div>

            {/* mobile menu */}
            <ul className={!nav ? 'hidden' : 'absolute top-0 left-0 w-full h-screen bg-[#0a192f] flex flex-col justify-center items-center'}>
                <li className='py-6 text-4xl hover:text-red-500'>
                    <Link onClick={handleClick} to="home" smooth={true} duration={500}>
                        Home
                    </Link>
                </li>
                <li className='py-6 text-4xl hover:text-red-500'> 
                    <Link onClick={handleClick} to="about" smooth={true} duration={500}>
                        About
                    </Link>
                </li>
                <li className='py-6 text-4xl hover:text-red-500'>
                    <Link onClick={handleClick} to="skills" smooth={true} duration={500}>
                        Skills
                    </Link>
                </li>
                <li className='py-6 text-4xl hover:text-red-500'>
                    <Link onClick={handleClick} to="work" smooth={true} duration={500}>
                        Work
                    </Link>
                </li>
                <li className='py-6 text-4xl hover:text-red-500'>
                    <Link onClick={handleClick} to='contact' smooth={true} duration={500}>
                        Contact
                    </Link>
                </li>
            </ul>
            

            {/* social icons */}
            <div className='hidden lg:flex fixed flex-col top-[35%] left-0'>
                <ul>
                    <li className='w-[160px] h-[60px] flex justify-between items-center ml-[-100px] hover:ml-[-10px] duration-300 bg-blue-600'>
                        <a className='flex justify-between items-center w-full text-gray-300' href="https://www.linkedin.com/in/mushtaq96/" target='_blank' rel="noopener noreferrer">
                            LinkedIn <FaLinkedin size={30}/>
                        </a>
                    </li>
                    <li className='w-[160px] h-[60px] flex justify-between items-center ml-[-100px] hover:ml-[-10px] duration-300 bg-[#33333]'>
                        <a className='flex justify-between items-center w-full text-gray-300' href="https://github.com/mushtaq96" target='_blank' rel="noopener noreferrer">
                            Github <FaGithub size={30}/>
                        </a>
                    </li>
                    <li className='w-[160px] h-[60px] flex justify-between items-center ml-[-100px] hover:ml-[-10px] duration-300 bg-green-900'>
                        <a className='flex justify-between items-center w-full text-gray-300' href="mailto:mushtaq96smb@gmail.com?subject=Important!&body=Hi.">
                            Email <HiOutlineMail size={30}/>
                        </a>
                    </li>
                    {/* <li className='w-[160px] h-[60px] flex justify-between items-center ml-[-100px] hover:ml-[-10px] duration-300 bg-gray-500'>
                        <a className='flex justify-between items-center w-full text-gray-300' href="https://drive.google.com/file/d/1YFpYQfXJki79ayEcpK56zSYBp4Ru4v4t/view?usp=sharing" target='_blank' rel="noopener noreferrer">
                            Resume <BsFillPersonLinesFill size={30}/>
                        </a>
                    </li> */}
                </ul>
            </div>
        </div>
    )
}

export default Navbar