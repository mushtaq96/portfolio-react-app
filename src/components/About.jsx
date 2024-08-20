import React from 'react';
import profileImage from '../assets/profile.jpg'; // Import your profile picture

const About = () => {
    return (
        <div name='about' className='w-full h-screen bg-[#0a192f] text-gray-300'>
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
                        <p>Worked in <span className='text-red-500'>Japan</span></p>
                        <p>Studying in <span className='text-red-500'>Germany</span></p>
                        <p>Hello there, I am Mushtaq</p>
                        <p className='text-xl font-normal'>Thanks for visiting, please take a look around</p>
                    </div>
                    <div>
                        <p>I'm a skilled AI/Machine Learning Engineer with a proven track record in crafting insightful, engaging, and functional web applications.</p>
                        <br />
                        <p> Drawing on my experience as a Backend Developer, Deep Learning Engineer and Full-Stack Developer, I bring a keen observer's mindset to unravel the intricacies of how things work. 
                            In addition to my proficiency in Python, JavaScript/TypeScript, I actively engage with machine learning and artificial intelligence to stay at the forefront of technological innovation.</p>
                        <br />
                        <p>Outside of work, I'm a passionate participant in the web3 space and contribute to various open-source projects. I also devote my time to volunteering activities, which broaden my perspective across different domains.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
