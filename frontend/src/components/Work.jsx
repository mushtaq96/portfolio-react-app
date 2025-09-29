// src/components/Work.jsx
import React from 'react'
import Opensea from '../assets/projects/opensea.png'
import Covid from '../assets/projects/covid.png'
import Comments from '../assets/projects/comments.png'
import Movie from '../assets/projects/movie.png'
import MoiveRecommentation from '../assets/projects/movie_recommendation.png'
import SearchPDF from '../assets/projects/search_pdf.png'

const Work = () => {
    return (
        <div name='work' className='w-full min-h-screen text-gray-300 bg-[#0a192f]'>
            <div className='max-w-[1000px] mx-auto p-4 flex flex-col justify-center w-full'>
                <div className=''>
                    <p className='text-4xl font-bold inline border-b-4 text-gray-300 border-red-600'>Work</p>
                    <p className='py-6'>// Check out some of my recent work</p>
                </div>
                {/* container */}
                <div className='grid sm:grid-cols-2 md:grid-cols-3 gap-4'>
                    {/* grid item - NFT Marketplace */}
                    <div
                        style={{ backgroundImage: `url(${Opensea})` }}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>
                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center p-2'> {/* Added p-2 for internal padding */}
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                NFT Marketplace (React Js)
                            </span>
                            {/* Added project description */}
                            <p className='text-white mt-2'>Full-stack NFT marketplace with blockchain integration.</p>
                            <div className='pt-4 text-center'> {/* Reduced pt from 8 to 4 for better spacing with new text */}
                                <a href="https://opensea-production.vercel.app/" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/opensea-blockchain-clone" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item - PyMovieRec */}
                     <div
                        style={{ backgroundImage: `url(${MoiveRecommentation})` }}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>
                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center p-2'> {/* Added p-2 for internal padding */}
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                PyMovieRec (Python)
                            </span>
                            {/* Added project description */}
                            <p className='text-white mt-2'>Python-based movie recommendation engine using ML.</p>
                            <div className='pt-4 text-center'> {/* Reduced pt from 8 to 4 for better spacing with new text */}
                                <a href="/">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/PyMovieRec" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item - Search PDF */}
                    <div
                        style={{ backgroundImage: `url(${SearchPDF})` }}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>
                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center p-2'> {/* Added p-2 for internal padding */}
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Search PDF (Python)
                            </span>
                            {/* Added project description */}
                            <p className='text-white mt-2'>AI-powered tool to ask questions about PDF content.</p>
                            <div className='pt-4 text-center'> {/* Reduced pt from 8 to 4 for better spacing with new text */}
                                <a href="/">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/search_pdf_llm">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item - Covid Tracker */}
                    <div
                        style={{ backgroundImage: `url(${Covid})` }}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>
                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center p-2'> {/* Added p-2 for internal padding */}
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Covid Tracker (React Js)
                            </span>
                            {/* Added project description */}
                            <p className='text-white mt-2'>Real-time COVID-19 data visualization dashboard.</p>
                            <div className='pt-4 text-center'> {/* Reduced pt from 8 to 4 for better spacing with new text */}
                                <a href="https://my-coronatracker.herokuapp.com/" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/corona-tracker" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item - Source Code Comments */}
                    <div
                        style={{ backgroundImage: `url(${Comments})` }}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>
                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center p-2'> {/* Added p-2 for internal padding */}
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Source Code (Python)
                            </span>
                            {/* Added project description */}
                            <p className='text-white mt-2'>Python script to analyze source code comments.</p>
                            <div className='pt-4 text-center'> {/* Reduced pt from 8 to 4 for better spacing with new text */}
                                <a href="https://cryptic-refuge-46980.herokuapp.com/" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Demo</button>
                                </a>
                                <a href="https://github.com/mushtaq96/source-comments" target="_blank" rel="noreferrer">
                                    <button className='text-center rounded-lg px-4 py-3 m-2 bg-white text-gray-700 font-bold text-lg'>Code</button>
                                </a>
                            </div>
                        </div>
                    </div>

                    {/* grid item - Movie Database */}
                    <div
                        style={{ backgroundImage: `url(${Movie})` }}
                        className='shadow-lg shadow-[#040c16] group container rounded-md flex justify-center items-center mx-auto content-div'>
                        {/* Hover effects */}
                        <div className='opacity-0 group-hover:opacity-100 text-center p-2'> {/* Added p-2 for internal padding */}
                            <span className='text-2xl font-bold text-white tracking-wider'>
                                Movie Database(React JS)
                            </span>
                            {/* Added project description */}
                            <p className='text-white mt-2'>Interactive movie search and information web app.</p>
                            <div className='pt-4 text-center'> {/* Reduced pt from 8 to 4 for better spacing with new text */}
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