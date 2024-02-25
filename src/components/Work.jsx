import React from 'react'
import WorkImg from '../assets/workImg.jpeg'
import realEstate from '../assets/realestate.jpg'
import Opensea from '../assets/projects/opensea.png'
import Covid from '../assets/projects/covid.png'
import Comments from '../assets/projects/comments.png'
import Movie from '../assets/projects/movie.png'
import MoiveRecommentation from '../assets/projects/movie_recommendation.png'
import SearchPDF from '../assets/projects/search_pdf.png'

const Work = () => {
    return (
        <div name='work' className='w-full md:h-screen text-gray-300 bg-[#0a192f]'>
            <div className='max-w-[1000px] mx-auto p-4 flex flex-col justify-center w-full'>
                <div className=''>
                    <p className='text-4xl font-bold inline border-b-4 text-gray-300 border-red-600'>Work</p>
                    <p className='py-6'>// Check out some of my recent work</p>
                </div>

                {/* container */}
                <div className='grid sm:grid-cols-2 md:grid-cols-3 gap-4'>

                    {/* grid item */}
                    <div  
                        style={{backgroundImage:`url(${Opensea})`}}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>

                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center'> 
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                NFT Marketplace (React Js)
                            </span>
                            <div className='pt-8 text-center'>
                                <a href="https://opensea-production.vercel.app/" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/opensea-blockchain-clone" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                     {/* grid item */}
                     <div  
                        style={{backgroundImage:`url(${MoiveRecommentation})`}}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>

                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100'> 
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                PyMovieRec (Python)
                            </span>
                            <div className='pt-8 text-center'>
                                <a href="/">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/PyMovieRec" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item */}
                    <div  
                        style={{backgroundImage:`url(${SearchPDF})`}}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>

                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100'> 
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Search PDF (Python)
                            </span>
                            <div className='pt-8 text-center'>
                                <a href="/">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/search_pdf_llm">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item */}
                    <div  
                        style={{backgroundImage:`url(${Covid})`}}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>

                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center'> 
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Covid Tracker (React Js)
                            </span>
                            <div className='pt-8 text-center'>
                                <a href="https://my-coronatracker.herokuapp.com/" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/corona-tracker" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item */}
                    <div  
                        style={{backgroundImage:`url(${Comments})`}}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>

                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center'> 
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Source Code (Python)
                            </span>
                            <div className='pt-8 text-center'>
                                <a href="https://cryptic-refuge-46980.herokuapp.com/" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/source-comments" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item */}
                    <div  
                        style={{backgroundImage:`url(${Movie})`}}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>

                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center'> 
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Movie Database(React JS)
                            </span>
                            <div className='pt-8 text-center'>
                                <a href="https://my-movie-search-webapp.herokuapp.com/" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/my-movie-search-webapp" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}

export default Work;