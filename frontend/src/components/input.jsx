import React from 'react';

export default function Input({ title, children }) {
    return (
      <div className="flex w-fit border border-neutral-800 rounded overflow-hidden text-white">
        <div className="flex items-center justify-center px-6 py-3 border-r border-neutral-800 bg-neutral-800 w-36">
          {title}
        </div>
  
        <div className="flex items-center gap-2 px-6 py-3 bg-neutral-900">
          {children}
        </div>
      </div>
    );
  }


