# IBM Plex Sans Condensed Font Setup

## 🎯 How to Add IBM Plex Sans Condensed Extra Light Font

### **Step 1: Download the Font Files**
You need to download the IBM Plex Sans Condensed Extra Light (200) font files:

**Required Files:**
- `IBMPlexSansCondensed-ExtraLight.woff2` (Web Open Font Format 2.0 - best quality)
- `IBMPlexSansCondensed-ExtraLight.woff` (Web Open Font Format - fallback)

### **Step 2: Download Sources**

#### **Option A: Official IBM Plex Fonts**
1. Go to [IBM Plex Fonts](https://www.ibm.com/plex/)
2. Download the IBM Plex Sans Condensed package
3. Extract and find the Extra Light (200) weight files

#### **Option B: Google Fonts (Alternative)**
If you prefer, you can use Google Fonts version:
```tsx
import { IBM_Plex_Sans_Condensed } from 'next/font/google';

const ibmPlexCondensed = IBM_Plex_Sans_Condensed({
  weight: ['200'],
  subsets: ['latin'],
  variable: '--font-ibm-plex-condensed',
});
```

### **Step 3: Place Font Files**
Put your font files in this directory:
```
web/public/fonts/
├── IBMPlexSansCondensed-ExtraLight.woff2
├── IBMPlexSansCondensed-ExtraLight.woff
└── README.md
```

### **Step 4: Font is Ready!**
The font will automatically be used throughout your app with:
- **Primary font**: IBM Plex Sans Condensed Extra Light (200)
- **Fallback**: System fonts if IBM Plex fails to load
- **All text elements**: Headings, body text, buttons, etc.

## 🎨 Font Characteristics
- **Style**: Condensed, modern, professional
- **Weight**: Extra Light (200) - very thin and elegant
- **Perfect for**: Professional applications, modern UI, clean design
- **Readability**: Excellent for both headings and body text

## 🔧 Customization
You can modify the font weight by:
1. Downloading different weight files (100, 300, 400, 500, 600, 700)
2. Updating the `@font-face` declarations in `globals.css`
3. Adjusting the `font-weight` values in your CSS classes
