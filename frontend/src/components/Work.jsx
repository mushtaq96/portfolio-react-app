// src/components/Work.jsx
import React from 'react'
import { FaRobot, FaGithub, FaExternalLinkAlt } from 'react-icons/fa'
import Opensea from '../assets/projects/opensea.png'
import MovieRec from '../assets/projects/movie_recommendation.png'
import SearchPDF from '../assets/projects/search_pdf.png'

// Only include a Demo link when the deployment is actually live (the NFT demo
// returned HTTP 200 when last checked). The old Heroku and href="/" demos were
// removed: a dead demo hurts trust more than no demo.
const projects = [
    {
        title: 'NFT Marketplace',
        description: 'Full-stack NFT marketplace with wallet connection and on-chain listing/buying.',
        tech: ['React', 'Blockchain'],
        image: Opensea,
        demo: 'https://opensea-production.vercel.app/',
        code: 'https://github.com/mushtaq96/opensea-blockchain-clone',
    },
    {
        title: 'Search PDF',
        description: 'Ask natural-language questions about a PDF and get grounded answers (RAG).',
        tech: ['Python', 'LLM', 'RAG'],
        image: SearchPDF,
        code: 'https://github.com/mushtaq96/search_pdf_llm',
    },
    {
        title: 'PyMovieRec',
        description: 'Content-based movie recommendation engine.',
        tech: ['Python', 'ML'],
        image: MovieRec,
        code: 'https://github.com/mushtaq96/PyMovieRec',
    },
]

// Older or smaller projects: linked, not showcased.
const moreProjects = [
    { title: 'COVID-19 Tracker', href: 'https://github.com/mushtaq96/corona-tracker' },
    { title: 'Movie Database', href: 'https://github.com/mushtaq96/my-movie-search-webapp' },
    { title: 'Source Code Comment Analyzer', href: 'https://github.com/mushtaq96/source-comments' },
]

const TechTags = ({ tech }) => (
    <div className='flex flex-wrap gap-2 mt-3'>
        {tech.map((t) => (
            <span key={t} className='text-xs px-2 py-1 rounded bg-gray-700/70 text-gray-200 border border-gray-600'>
                {t}
            </span>
        ))}
    </div>
)

const LinkButtons = ({ demo, code, onDemo }) => (
    <div className='flex flex-wrap gap-3 mt-4'>
        {onDemo && (
            <button
                onClick={onDemo}
                className='inline-flex items-center gap-2 rounded px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold'
            >
                Try it live <FaExternalLinkAlt size={12} />
            </button>
        )}
        {demo && (
            <a href={demo} target='_blank' rel='noreferrer'
               className='inline-flex items-center gap-2 rounded px-3 py-2 bg-white text-gray-800 hover:bg-gray-200 text-sm font-semibold'>
                Live Demo <FaExternalLinkAlt size={12} />
            </a>
        )}
        {code && (
            <a href={code} target='_blank' rel='noreferrer'
               className='inline-flex items-center gap-2 rounded px-3 py-2 border border-gray-500 text-gray-200 hover:bg-gray-700 text-sm font-semibold'>
                Code <FaGithub size={14} />
            </a>
        )}
    </div>
)

const Work = () => {
    const openChatbot = () => window.dispatchEvent(new CustomEvent('openChatbot'))

    return (
        <div name='work' className='w-full min-h-screen text-gray-300 bg-[#0a192f]'>
            <div className='max-w-[1000px] mx-auto px-4 py-12 flex flex-col justify-center w-full'>
                <div>
                    <p className='text-4xl font-bold inline border-b-4 text-gray-300 border-red-600'>Work</p>
                    <p className='py-6 text-gray-400'>// Selected projects — the featured one is running on this page</p>
                </div>

                {/* Featured project: the RAG assistant powering this site */}
                <div className='rounded-lg border border-red-600 bg-gradient-to-br from-gray-800/70 to-[#0a192f] p-6 mb-8'>
                    <div className='flex items-center gap-3'>
                        <FaRobot className='text-red-500' size={28} />
                        <h3 className='text-2xl font-bold text-gray-100'>AI Portfolio Assistant <span className='text-red-400'>(RAG)</span></h3>
                        <span className='ml-auto text-xs uppercase tracking-wider text-red-400 border border-red-600 rounded px-2 py-1'>Featured</span>
                    </div>
                    <p className='mt-3 text-gray-300 max-w-[720px]'>
                        The assistant on this page. Ask it about my background in English or German — it retrieves
                        relevant chunks from my CV with a vector search and answers with an LLM. Built as three
                        deployable services (frontend, RAG backend, embedding API).
                    </p>
                    <TechTags tech={['FastAPI', 'ChromaDB', 'sentence-transformers', 'Groq / Llama 3.1', 'React']} />
                    <LinkButtons
                        onDemo={openChatbot}
                        code='https://github.com/mushtaq96/portfolio-react-app'
                    />
                </div>

                {/* Grid of remaining projects */}
                <div className='grid sm:grid-cols-2 md:grid-cols-3 gap-6'>
                    {projects.map((p) => (
                        <div key={p.title} className='flex flex-col rounded-md overflow-hidden bg-gray-800/40 shadow-lg shadow-[#040c16]'>
                            <img src={p.image} alt={`${p.title} screenshot`} className='w-full h-40 object-cover' />
                            <div className='flex flex-col flex-1 p-4'>
                                <h3 className='text-lg font-bold text-gray-100'>{p.title}</h3>
                                <p className='text-sm text-gray-400 mt-1'>{p.description}</p>
                                <TechTags tech={p.tech} />
                                <div className='mt-auto'>
                                    <LinkButtons demo={p.demo} code={p.code} />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <p className='mt-8 text-sm text-gray-400'>
                    Older projects:{' '}
                    {moreProjects.map((p, i) => (
                        <React.Fragment key={p.title}>
                            {i > 0 && ' · '}
                            <a href={p.href} target='_blank' rel='noreferrer' className='text-red-400 hover:text-red-300 underline'>{p.title}</a>
                        </React.Fragment>
                    ))}
                    {' · '}
                    <a href='https://github.com/mushtaq96' target='_blank' rel='noreferrer' className='text-red-400 hover:text-red-300 underline'>all on GitHub</a>
                </p>
            </div>
        </div>
    )
}

export default Work;
