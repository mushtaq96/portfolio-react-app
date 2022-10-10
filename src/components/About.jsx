import React from 'react'

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
                    <div>

                    </div>
                </div>

                <div className='max-w-[1000px] w-full grid sm:grid-cols-2 gap-8 px-4'>
                    <div className='sm:text-right text-4xl font-bold'>
                       
                        <p>Born in India</p>
                        <p>Worked in Japan</p>
                        <p>Studying in Germany</p>
                        <p>Hello there, I am Mushtaq</p>
                        <p className='text-xl font-normal'>Thanks for visiting, please take a look around</p>
                    </div>
                    <div>
                        <p>Am a keen observer and enjoy figuring out how things work. </p>
                        <p>Enjoy making insightful, engaging and functional web apps with a clean, simple and distinctive designs.</p>
                        <br></br>
                        <p>In my previous work experiences I have donned the roles of a .Net/C# Dev, Backend Dev and Junior Full-Stack Dev. </p>
                        <p>In my personal time I am involved with technologies such as Javascript/Typescript, Python, React and more.</p>
                        <br></br>
                        <p>I am also an active participant in the web3 space.</p>
                        <p>Love to be involved in volunteering activities which help me broaden my perspective of things either of my domain or from different domains.
                        </p>
                    </div>
                </div>
            </div>
        </div>

    );
};

export default About;