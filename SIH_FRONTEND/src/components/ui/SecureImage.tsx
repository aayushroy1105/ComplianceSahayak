import React, { useState, useEffect } from 'react';

interface SecureImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
}

const SecureImage: React.FC<SecureImageProps> = ({ src, alt, ...props }) => {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let urlToRevoke: string | null = null;
    
    if (!src) return;
    
    const fetchImage = async () => {
      try {
        const response = await fetch(src, {
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch image: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setObjectUrl(url);
        urlToRevoke = url;
      } catch (err) {
        console.error("SecureImage fetch error:", err);
        setError(true);
      }
    };
    
    fetchImage();
    
    return () => {
      if (urlToRevoke) {
        URL.revokeObjectURL(urlToRevoke);
      }
    };
  }, [src]);

  if (error || !src) {
    return (
      <div className={`flex items-center justify-center bg-slate-100 text-slate-400 ${props.className || ''}`} style={props.style}>
        <span>{alt || 'Image Error'}</span>
      </div>
    );
  }

  if (!objectUrl) {
    return (
      <div className={`flex items-center justify-center bg-slate-50 text-slate-400 animate-pulse ${props.className || ''}`} style={props.style}>
        <span>Loading...</span>
      </div>
    );
  }

  return <img src={objectUrl} alt={alt} {...props} />;
};

export default SecureImage;
