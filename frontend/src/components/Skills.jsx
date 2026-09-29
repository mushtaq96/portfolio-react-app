import React from 'react'

import Javascript from '../assets/javascript.png';
import ReactImg from '../assets/react.png';
import Node from '../assets/node.png';
import Tailwind from '../assets/tailwind.png';
import Python from '../assets/python.png';
import MySQL from '../assets/mysql.png';
import CSharp from '../assets/cSharp.png';
import Git from '../assets/github.svg';
import Docker from '../assets/docker.svg';
import Kubernetes from '../assets/kubernetes.svg';
import MicrosoftAzure from '../assets/azure.svg';
import Aws from '../assets/aws.png';

// Grouped by the roles being targeted (backend/platform first). Only skills that
// appear on the CV are listed; an item with no `icon` renders as a text chip.
const groups = [
    {
        title: 'Backend & APIs',
        items: [
            { name: 'C# / .NET', icon: CSharp },
            { name: 'ASP.NET Core' },
            { name: 'Python', icon: Python },
            { name: 'Node.js', icon: Node },
            { name: 'REST' },
            { name: 'GraphQL' },
            { name: 'Microservices' },
            { name: 'TDD / xUnit' },
        ],
    },
    {
        title: 'Cloud & Platform',
        items: [
            { name: 'Azure', icon: MicrosoftAzure },
            { name: 'AWS', icon: Aws },
            { name: 'Docker', icon: Docker },
            { name: 'Kubernetes', icon: Kubernetes },
            { name: 'CI/CD' },
            { name: 'Terraform' },
            { name: 'Git / GitHub', icon: Git },
        ],
    },
    {
        title: 'Data & ML',
        items: [
            { name: 'PostgreSQL' },
            { name: 'SQL Server' },
            { name: 'MongoDB' },
            { name: 'MySQL', icon: MySQL },
            { name: 'RAG & embeddings' },
            { name: 'Transfer learning' },
        ],
    },
    {
        title: 'Frontend',
        items: [
            { name: 'React', icon: ReactImg },
            { name: 'JavaScript', icon: Javascript },
            { name: 'TypeScript' },
            { name: 'Tailwind', icon: Tailwind },
            { name: 'HTML / CSS' },
        ],
    },
];

const Skills = () =>{
    return (
        <div name='skills' className='w-full min-h-screen bg-[#0a192f] text-gray-300'>
            {/* container */}
            <div className='max-w-[1000px] mx-auto px-4 py-12 flex flex-col justify-center w-full h-full'>
                <div>
                    <p className='text-4xl font-bold inline border-b-4 border-red-600'>Skills</p>
                    <p className='py-4 text-gray-400'>{'// Technologies I have worked with, grouped by focus'}</p>
                </div>

                <div className='grid sm:grid-cols-2 gap-6 py-6'>
                    {groups.map((g) => (
                        <div key={g.title} className='rounded-md border border-gray-700 bg-gray-800/30 p-5'>
                            <h3 className='text-lg font-bold text-gray-100'>{g.title}</h3>
                            <div className='flex flex-wrap gap-2 mt-4'>
                                {g.items.map((item) => (
                                    <span
                                        key={item.name}
                                        className='inline-flex items-center gap-2 rounded px-3 py-1.5 text-sm bg-gray-700/60 text-gray-200 border border-gray-600'
                                    >
                                        {item.icon && <img src={item.icon} alt='' className='w-5 h-5 object-contain' />}
                                        {item.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Skills;
