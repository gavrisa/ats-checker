import React from 'react';

// Example of how to use your custom uploaded icons
export const CustomIcon1: React.FC<{ className?: string }> = ({ className = "h-6 w-6" }) => (
  <img 
    src="/icons/your-icon-1.svg" 
    alt="Custom Icon 1" 
    className={className}
  />
);

export const CustomIcon2: React.FC<{ className?: string }> = ({ className = "h-6 w-6" }) => (
  <img 
    src="/icons/your-icon-2.svg" 
    alt="Custom Icon 2" 
    className={className}
  />
);

export const CustomIcon3: React.FC<{ className?: string }> = ({ className = "h-6 w-6" }) => (
  <img 
    src="/icons/your-icon-3.svg" 
    alt="Custom Icon 3" 
    className={className}
  />
);

// Alternative: If you want to use them as background images
export const CustomIcon1Bg: React.FC<{ className?: string }> = ({ className = "h-6 w-6" }) => (
  <div 
    className={`bg-contain bg-no-repeat bg-center ${className}`}
    style={{ backgroundImage: 'url(/icons/your-icon-1.svg)' }}
  />
);
