import React from 'react'

import HTML from '../assets/html.png';
import CSS from '../assets/css.png';
import Javascript from '../assets/javascript.png';
import ReactImg from '../assets/react.png';
import Node from '../assets/node.png';
import Tailwind from '../assets/tailwind.png';
import Python from '../assets/python.png';
import Mongo from '../assets/tailwind.png';
import MySQL from '../assets/mysql.png';
import Pytorch from '../assets/pytorch.svg';
import Git from '../assets/github.svg';
import Docker from '../assets/docker.svg';
import Kubernetes from '../assets/kubernetes.svg';
import MicrosoftAzure from '../assets/azure.svg';

const Skills = () =>{
    return (
        <div name='skills' className='w-full min-h-screen bg-[#0a192f] text-gray-300'>
            {/* container */}
            <div className='max-w-[1000px] mx-auto p-4 flex flex-col justify-center w-full h-full'>
                <div>
                    <p className='text-4xl font-bold inline border-b-4 border-red-600'>Skills</p>
                    <p className='py-4'>// These are some of the technologies I have worked with</p>
                </div>

                <div className='w-full grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 text-center py-8'>


                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={Python} alt="Python icon"/>
                        <p className='my-4'>Python</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={Pytorch} alt="Pytorch icon"/>
                        <p className='my-4'>Pytorch</p>
                    </div>
                   
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={MicrosoftAzure} alt="MicrosoftAzure icon"/>
                        <p className='my-4'>Microsoft Azure</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={Kubernetes} alt="Kubernetes icon"/>
                        <p className='my-4'>Kubernetes</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={Docker} alt="Docker icon"/>
                        <p className='my-4'>Docker</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={Mongo} alt="Mongo icon"/>
                        <p className='my-4'>Mongo Db</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={MySQL} alt="MySQL icon"/>
                        <p className='my-4'>MySQL</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={HTML} alt="HTML icon"/>
                        <p className='my-4'>HTML</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={CSS} alt="CSS icon"/>
                        <p className='my-4'>CSS</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={Javascript} alt="Javascript icon"/>
                        <p className='my-4'>Javascript</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={ReactImg} alt="React icon"/>
                        <p className='my-4'>React</p>
                    </div>
                    <div className='shadow-md shadow-[#040c16] hover:scale-110 duration-500'>
                        <img className='w-20 mx-auto' src={Node} alt="Node icon"/>
                        <p className='my-4'>NodeJs</p>
                    </div>
                   
              

                </div>
                
            </div>
        </div>
    )
}

export default Skills;