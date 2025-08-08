# Favicon Creation Instructions

To create a proper favicon.ico from your coingrok-logo-icon.png:

## Method 1: Online Converter (Recommended)
1. Go to https://favicon.io/favicon-converter/
2. Upload your `coingrok-logo-icon.png`
3. Download the generated favicon.ico
4. Place it in the `/public/` directory (not in logos folder)

## Method 2: Using ImageMagick (Command Line)
```bash
# Install ImageMagick if not already installed
brew install imagemagick

# Convert PNG to ICO
convert /Users/alexandrugabrielmihai/Desktop/everything/CoinGrok/CoinGrok-mvp/frontend/public/logos/coingrok-logo-icon.png -resize 16x16 -resize 32x32 -resize 48x48 /Users/alexandrugabrielmihai/Desktop/everything/CoinGrok/CoinGrok-mvp/frontend/public/favicon.ico
```

## Method 3: Manual Creation
1. Open your coingrok-logo-icon.png in an image editor
2. Resize to 32x32 pixels (maintaining aspect ratio)
3. Save/Export as favicon.ico format
4. Place in the `/public/` directory

## Final Step
Once you have favicon.ico in the public folder, update the layout.tsx icons metadata to include:
```typescript
icons: {
  icon: '/favicon.ico',
  shortcut: '/favicon.ico',
  apple: '/logos/coingrok-logo-icon.png',
},
```