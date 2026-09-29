import React from 'react'
import {HiArrowNarrowRight} from 'react-icons/hi'
import { FaRobot, FaFileDownload } from 'react-icons/fa';
import { scroller } from 'react-scroll'

// TODO: verify this points to your latest CV (the old Google Drive link).
const CV_URL = 'https://drive.google.com/file/d/1YFpYQfXJki79ayEcpK56zSYBp4Ru4v4t/view?usp=sharing';

const Home = ({ showChatbot }) => {
    return (
        <div name='home' className='w-full h-screen bg-[#0a192f]'>

            {/* Container */}
            <div className='max-w-[1000px] mx-auto px-4 sm:px-6 md:px-8 flex flex-col justify-center h-full'>
                <p className='text-red-500'> Hi, my name is </p>
                <h1 className='text-3xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-[#bbc4e2]'>SM Mushtaq Bokhari.</h1>
                <h2 className='text-3xl sm:text-5xl font-bold text-[#8892b0]'>
                    Senior Full-Stack &amp; Backend Engineer.
                </h2>
                <p className='text-[#8892b0] py-4 max-w-[700px]'>
                    5+ years building ML-driven backend systems in <span className='text-red-500'>C#/.NET</span>,{' '}
                    <span className='text-red-500'>Python</span> and <span className='text-red-500'>Azure</span> —
                    including at <span className='text-gray-200 font-semibold'>Mercedes-Benz R&amp;D</span> and{' '}
                    <span className='text-gray-200 font-semibold'>CGI</span>.
                    <br />
                    Work authorization for Germany · German B2 · English C2. Open to <span className='text-red-500'>full-time</span> roles.
                </p>
                <div className='flex flex-wrap items-center gap-2'>
                    {/* A real button (keyboard-focusable) instead of a button nested in react-scroll's href-less <a>. */}
                    <button
                        onClick={() => scroller.scrollTo('work', { smooth: true, duration: 500, offset: -80 })}
                        className='text-white group border-2 px-6 py-3 my-2 flex items-center hover:bg-red-600 hover:border-red-600 rounded'
                    >
                        View Work
                        <span className='group-hover:rotate-90 duration-300'>
                            <HiArrowNarrowRight className='ml-3'/>
                        </span>
                    </button>
                    <a
                        href={CV_URL}
                        target="_blank"
                        rel="noreferrer"
                        className='text-white group border-2 border-gray-500 px-6 py-3 my-2 flex items-center hover:bg-gray-700 hover:border-gray-700 rounded'
                    >
                        Download CV
                        <FaFileDownload className='ml-3 group-hover:translate-y-0.5 duration-300' />
                    </a>
                </div>
                {/* AI assistant teaser */}
                { !showChatbot && (
                <div className="mt-6 p-3 bg-gray-800 bg-opacity-50 rounded-lg border border-red-600 text-sm flex items-start">
                    <FaRobot className="text-red-500 mr-2 mt-1 flex-shrink-0" />
                    <p className="text-gray-300">Curious about my background? Ask my AI assistant! <button onClick={() => window.dispatchEvent(new CustomEvent('openChatbot'))} className="text-red-400 hover:text-red-300 underline ml-1">Click here to chat.</button></p>
                </div>
                )}
            </div>
        </div>
    )
}

export default Home