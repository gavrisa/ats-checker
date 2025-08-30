# Custom Icons Usage Guide

## 🎯 How to Add Your Custom Icons

### **Step 1: Upload Your Icons**
1. Place your 3 custom icon files in `web/public/icons/`
2. Supported formats: SVG, PNG, WebP, JPG
3. Recommended: SVG for best quality and scalability

### **Step 2: Use in Your Code**

#### **Option A: Direct Image Tags**
```tsx
<img src="/icons/your-icon-name.svg" alt="Description" className="h-6 w-6" />
```

#### **Option B: React Components (Recommended)**
```tsx
import { CustomIcon1, CustomIcon2, CustomIcon3 } from './components/icons/CustomIcons';

// Use in your JSX
<CustomIcon1 className="h-8 w-8" />
<CustomIcon2 className="h-6 w-6" />
<CustomIcon3 className="h-5 w-5" />
```

#### **Option C: Background Images**
```tsx
<div 
  className="h-6 w-6 bg-contain bg-no-repeat bg-center"
  style={{ backgroundImage: 'url(/icons/your-icon-name.svg)' }}
/>
```

## 📁 File Structure
```
web/
├── public/
│   └── icons/
│       ├── your-icon-1.svg
│       ├── your-icon-2.svg
│       └── your-icon-3.svg
└── components/
    └── icons/
        ├── CustomIcons.tsx
        └── README.md
```

## 🎨 Icon Best Practices
- **SVG format**: Best for scalability and quality
- **Consistent sizing**: Use consistent dimensions
- **Alt text**: Always provide descriptive alt text
- **Responsive**: Use responsive classes like `h-6 w-6 lg:h-8 lg:w-8`

## 🔧 Customization
You can modify the `CustomIcons.tsx` file to:
- Change default sizes
- Add hover effects
- Include animations
- Customize colors
