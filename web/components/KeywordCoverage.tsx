import React from 'react';

interface KeywordCoverageProps {
  current: number;
  total: number;
  screenWidth?: number;
  animatedPercent?: number;
  animatedBarWidth?: number;
}

const KeywordCoverage: React.FC<KeywordCoverageProps> = ({ current, total, screenWidth = 1920, animatedPercent, animatedBarWidth }) => {
  const rawPercent = (current / total) * 100;
  const percent = rawPercent === 0 ? 0 : Math.max(1, Math.round(rawPercent));
  
  // Use animated percent if provided, otherwise use calculated percent
  const displayPercent = animatedPercent !== undefined ? animatedPercent : percent;
  
  // Use animated bar width if provided, otherwise use calculated percent
  const displayBarWidth = animatedBarWidth !== undefined ? animatedBarWidth : percent;
  
  // Determine status and color based on percentage
  const getStatusInfo = (percent: number) => {
    if (percent < 70) {
      return { text: 'needs improvement', color: '#E7640E' };
    } else {
      return { text: 'good', color: '#97CC6D' };
    }
  };

  // Get progress bar colors based on status
  const getProgressBarColors = (percent: number) => {
    if (percent < 70) {
      return {
        primary: '#E65C01',
        secondary: '#FF8A50'
      };
    } else {
      return {
        primary: '#97CC6D',
        secondary: '#B8E6A0'
      };
    }
  };

  const statusInfo = getStatusInfo(percent);

  return (
    <div 
      style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        gap: '18px',
        width: '100%',
        minWidth: '0',
        position: 'relative',
        alignSelf: 'stretch'
      }}
    >
      {/* Left: Keywords + Percentage */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0px', flexShrink: 0 }}>
        <div 
          className="font-ibm-condensed font-extralight text-[#737373]" 
          style={{
            fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px',
            fontVariantNumeric: 'tabular-nums'
          }}
          aria-live="polite"
          aria-label={`${current} out of ${total} keywords`}
        >
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{current}</span>/{total} keywords
        </div>
        <div 
          className="font-ibm-condensed font-extralight text-[#000000] font-bold" 
          style={{
            fontSize: screenWidth <= 768 ? '24px' : screenWidth <= 1024 ? '32px' : '36px',
            fontVariantNumeric: 'tabular-nums',
            minWidth: '3ch', // Reserve space for 3 characters (e.g., "100")
            textAlign: 'left'
          }}
          aria-live="polite"
          aria-label={`${percent} percent coverage`}
        >
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{percent}</span>%
        </div>
      </div>

      {/* Center: Progress Bar */}
      <div style={{ 
        flex: '1 1 0%',
        minWidth: '0',
        width: '100%'
      }}>
        <div 
          style={{ 
            width: '100%', 
            backgroundColor: '#F2F2F2', 
            borderRadius: '8px', 
            height: '22px',
            position: 'relative',
            overflow: 'hidden'
          }}
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label="Keyword coverage"
        >
          <div 
            style={{
              height: '100%',
              borderRadius: '8px 0 0 8px',
              width: `${displayBarWidth}%`,
              backgroundColor: `${getProgressBarColors(percent).primary}`,
              position: 'relative',
              transition: 'none', // Disable CSS transition, use JS animation
              minWidth: '20px'
            }}
          >
            {/* White diagonal stripes overlay */}
            <div 
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: `repeating-linear-gradient(
                  -75deg,
                  transparent,
                  transparent 1px,
                  rgba(255, 255, 255, 0.8) 1px,
                  rgba(255, 255, 255, 0.8) 2px
                )`,
                borderRadius: '8px 0 0 8px'
              }}
            />
          </div>
        </div>
        

      </div>

      {/* Right: Status Label */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px', 
        flexShrink: 0 
      }}>
        <img 
          src={percent < 70 ? '/icons/Info.svg' : '/icons/check_circle.svg'}
          alt={percent < 70 ? 'needs improvement' : 'good'}
          style={{ 
            width: '16px', 
            height: '16px',
            filter: percent < 70 ? 'brightness(0) saturate(100%) invert(27%) sepia(51%) saturate(2878%) hue-rotate(346deg) brightness(104%) contrast(97%)' : 'brightness(0) saturate(100%) invert(67%) sepia(31%) saturate(638%) hue-rotate(86deg) brightness(95%) contrast(86%)'
          }}
        />
        <span style={{ 
          fontFamily: 'IBM Plex Sans Condensed', 
          fontWeight: '200', 
          fontSize: screenWidth <= 768 ? '12px' : screenWidth <= 1024 ? '13px' : '14px',
          color: statusInfo.color 
        }}>
          {statusInfo.text}
        </span>
      </div>
    </div>
  );
};

export default KeywordCoverage;
