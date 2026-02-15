import React from 'react';

const Loader = ({ message = 'Loading...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600"></div>
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
};

export default Loader;