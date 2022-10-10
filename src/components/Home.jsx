import React from 'react'
import {HiArrowNarrowRight} from 'react-icons/hi'
import { Link } from 'react-scroll'

const Home = () => {
    return (
        <div name='home' className='w-full h-screen bg-[#0a192f]'>

            {/* Container */}
            <div className='max-w-[1000px] mx-auto px-8 flex flex-col justify-center h-full'>
                <p className='#16e0bd text-red-300'> Hi, my name is </p>
                <h1 className='text-4xl sm:text-7xl font-bold text-[#bbc4e2]'>SM Musthaq bokhari</h1>
                <h2 className='text-4xl sm:text-7xl font-bold text-[#8892b0]'>I am a Full-stack devloper.</h2>
                <p className ='text-[#8892b0] py-4 max-w-[700px]'>
                    I am a Full-stack devloper specializing in building robust applications. Currently a masters student interested in volunteering.
                    I am focued on builing responsive full stack web applications
                </p>
                <div>
                    <Link to="work" smooth={true} duration={500}>
                        <button className='text-white group border-2 px-6 py-3 my-2 flex items-center hover:bg-red-600 hover:border-red-600'>
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