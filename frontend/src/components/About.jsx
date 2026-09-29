import React from 'react';
import profileImage from '../assets/profile.jpg'; // Import your profile picture

const About = () => {
    return (
        <div name='about' className='w-full min-h-screen p-2 bg-[#0a192f] text-gray-300'>
            <div className='flex flex-col justify-center items-center w-full h-full'>
                <div className='max-w-[1000px] w-full grid grid-cols-2 gap-8'>
                    <div className='flex flex-col justify-center'>
                       
                            <p className='text-4xl font-bold inline border-b-4 border-red-600 text-right'>
                                About
                            </p>
                       
                    </div>
                    <div>
                        {/* profile picture */}
                        <img src={profileImage} alt='Profile' className='w-full max-w-xs rounded-full mx-auto mb-4' />
                    </div>
                </div>

                <div className='max-w-[1000px] w-full grid sm:grid-cols-2 gap-8 px-4'>
                    <div className='sm:text-right text-4xl font-bold'>
                        <p>Born in <span className='text-red-500'>India</span></p>
                        <p>Sharpened in <span className='text-red-500'>Japan</span></p>
                        <p>Now building in <span className='text-red-500'>Germany</span></p>
                        <p className='mt-4'>Hi, I'm Mushtaq.</p>
                        <p className='text-xl font-normal mt-2'>
                            Three countries, three engineering cultures — one throughline: systems people can rely on.
                        </p>
                    </div>
                    <div>
                        <p>I'm a full-stack engineer who leans backend, with 5+ years turning messy real-world
                           problems into dependable services. My work sits where solid backend engineering meets
                           applied ML — systems that have to be correct, observable, and still ship on time.</p>
                        <br />
                        <p>That perspective is stitched together from three places. India gave me the fundamentals.
                           Four years in Tokyo taught me the discipline of maintaining systems other people depend
                           on — an enterprise order platform handling 1,000+ transactions a week, with test coverage
                           pushed past 80%. Germany — and a Master's at grade 1.4 — is where I moved into production
                           ML: image-processing models at <span className='text-gray-100 font-semibold'>Mercedes-Benz R&D</span>{' '}
                           (+20% accuracy) and at <span className='text-gray-100 font-semibold'>CGI</span>, a
                           communication-analysis platform that cut manual analysis time by ~60%.</p>
                        <br />
                        <p>Day to day that's C#/.NET, Python, and Azure, with React on the front when it's needed.
                           Outside the editor I've coordinated hackathons and led orientation for ~1,000 new
                           students, and I contribute to open source. I'm currently after senior backend / platform
                           roles — English C2, German B2, conversational Japanese.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
