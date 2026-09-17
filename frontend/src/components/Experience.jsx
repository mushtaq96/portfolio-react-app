import React from 'react';

// One quantified line per role — the numbers come straight from your CV.
// Keep these honest and verifiable; recruiters (especially in DE/CH) probe them.
const roles = [
    {
        company: 'CGI',
        role: 'Full-Stack AI Engineer',
        location: 'Frankfurt, Germany',
        period: 'Apr 2025 – Present',
        impact: 'Built an AI communication-analysis platform (C#/ASP.NET Core, React, Azure) that cut manual analysis time by ~60%.',
    },
    {
        company: 'Mercedes-Benz R&D',
        role: 'AI Engineer',
        location: 'Stuttgart, Germany',
        period: 'Sep 2023 – Aug 2024',
        impact: 'Optimized automotive image-processing models with transfer learning, raising classification accuracy by +20%.',
    },
    {
        company: 'Mercedes-Benz',
        role: 'Full-Stack Developer',
        location: 'Stuttgart, Germany',
        period: 'Mar 2023 – Aug 2023',
        impact: 'Shipped a real-time production-data dashboard (Python microservices, TypeScript/Next.js); introduced SSR for −30% response times.',
    },
    {
        company: 'Zenken Corporation',
        role: 'Full-Stack Developer',
        location: 'Tokyo, Japan',
        period: 'Nov 2018 – Feb 2022',
        impact: 'Maintained an enterprise order system (>1,000 transactions/week) and raised automated-test coverage above 80%, saving ~20 dev-hours/month.',
    },
];

const Experience = () => {
    return (
        <div name='experience' className='w-full min-h-screen bg-[#0a192f] text-gray-300'>
            <div className='max-w-[1000px] mx-auto p-4 flex flex-col justify-center w-full h-full'>
                <div>
                    <p className='text-4xl font-bold inline border-b-4 border-red-600'>Experience</p>
                    <p className='py-4 text-gray-400'>// Where I've worked and the impact I shipped</p>
                </div>

                <div className='mt-6 space-y-4'>
                    {roles.map((r) => (
                        <div
                            key={`${r.company}-${r.period}`}
                            className='border-l-4 border-red-600 bg-gray-800/40 rounded-r-md p-4 hover:bg-gray-800/70 duration-300'
                        >
                            <div className='flex flex-col sm:flex-row sm:items-baseline sm:justify-between'>
                                <h3 className='text-xl font-bold text-gray-100'>
                                    {r.role} · <span className='text-red-400'>{r.company}</span>
                                </h3>
                                <span className='text-sm text-gray-400'>{r.period}</span>
                            </div>
                            <p className='text-sm text-gray-500'>{r.location}</p>
                            <p className='mt-2 text-gray-300'>{r.impact}</p>
                        </div>
                    ))}
                </div>

                <p className='mt-6 text-gray-400 text-sm'>
                    M.Eng. Software Engineering, Hochschule Hof (final grade 1.4) · Azure certified (AI-900, AI-102)
                </p>
            </div>
        </div>
    );
};

export default Experience;
