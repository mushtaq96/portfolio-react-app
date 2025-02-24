import React from 'react'
import {HiArrowNarrowRight} from 'react-icons/hi'
import { Link } from 'react-scroll'

const Home = () => {
    return (
        <div name='home' className='w-full h-screen bg-[#0a192f]'>

            {/* Container */}
            <div className='max-w-[1000px] mx-auto px-4 sm:px-6 md:px-8 flex flex-col justify-center h-full'>
                <p className='text-red-500'> Hi, my name is </p>
                <h1 className='text-3xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-[#bbc4e2]'>SM Mushtaq Bokhari.</h1>
                <h2 className='text-3xl sm:text-5xl font-bold text-[#8892b0]'>I craft solutions for the AI &lt;<span className='text-red-500'>world</span>/&gt;.</h2>
                <p className ='text-[#8892b0] py-4 max-w-[700px]'>
                    I am a Software Developer who is curious by nature, empathy minded, passionate about leveraging technology to solve real-world problems. 
                    My focus lies in areas such as AI/Machine learning and Full Stack Development. 
                    Seeking <span className='text-red-500'>Full-Time</span> opportunities! 
                    <br/>
                   
                </p>
                <div>
                    <Link to="work" smooth={true} duration={500}>
                        <button className='text-white group border-2 px-6 py-3 my-2 flex items-center hover:bg-red-600 hover:border-red-600 rounded'>
                            View Work 
                            <span className='group-hover:rotate-90 duration-300'>
                                <HiArrowNarrowRight className='ml-3'/> 
                            </span>                       
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    )
}

export default Home