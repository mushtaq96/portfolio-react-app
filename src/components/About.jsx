import React from 'react';
import profileImage from '../assets/profile.jpg'; // Import your profile picture

const About = () => {
    return (
        <div name='about' className='w-full h-screen bg-[#0a192f] text-gray-300'>
            <div className='flex flex-col justify-center items-center w-full h-full'>
                <div className='max-w-[1000px] w-full grid grid-cols-2 gap-8'>
                    <div className='sm:text-right pb-8 pl-4'>
                        <p className='text-4xl font-bold inline border-b-4 border-red-600'>
                            About
                        </p>
                    </div>
                   
                </div>
                <div className='max-w-[1000px] w-full grid grid-cols-1 sm:grid-cols-2 gap-8 px-4'>
                    <div className='sm:text-right text-4xl font-bold'>
                        <img src={profileImage} alt='Profile' className='w-48 h-48 rounded-full mb-4 ml-auto object-contain' />
                        <p>Born in India</p>
                        <p>Worked in Japan</p>
                        <p>Studying in Germany</p>
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
