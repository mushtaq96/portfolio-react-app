import React from 'react'

const About = () => {
    return (
        <div name='about' className='w-full h-screen bg-[#0a192f] text-gray-300'>
            <div className='flex flex-col justify-center items-center w-full h-full'>
                <div className='max-w-[1000px] w-full grid grid-cols-2 gap-8'>
                    <div className='sm:text-right pb-8 pl-4'>
                        <p className='text-4xl font-bold inline border-b-4 border-pink-600'>
                            About
                        </p>
                    </div>
                    <div>

                    </div>
                </div>

                <div className='max-w-[1000px] w-full grid sm:grid-cols-2 gap-8 px-4'>
                    <div className='sm:text-right text-4xl font-bold'>
                        <p>Hi I am Mushtaq, nice to meet you. please take a look around</p>
                    </div>
                    <div>
                        <p>
                        Development
                        Professionally I work as .Net/C# developer. In my personal time I am involved with React and Python related pet projects.

                        Volunteering
                        I like to be involved in activities which help me broaden my perspective of things either of my domain or from different domains.
                        </p>
                    </div>
                </div>
            </div>
        </div>

    );
};

export default About;