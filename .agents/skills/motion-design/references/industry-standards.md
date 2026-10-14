# Industry Standards Overview

## The Standards Landscape

There is no single governing body for animation standards. The industry relies on:

1. **Design System Guidelines** — De facto standards (M3, Fluent, Carbon, Apple HIG)
2. **File Format Specifications** — Technical interchange (Lottie, dotLottie, W3C DTCG)
3. **Best Practice Consensus** — Shared across major companies

## Why Material Design 3 as Baseline

M3 is the closest to an "industry standard" because:

1. **Most comprehensive** — Complete motion specification with tokens
2. **Widely adopted** — Used as benchmark by Klarna, others
3. **Well documented** — Clear rationale for all values
4. **Cross-platform** — Android, Web, Flutter, iOS
5. **Open** — Publicly documented, free to use

## Standards Authority

| Domain | Authority | Documentation |
|--------|-----------|---------------|
| Token Format | W3C DTCG | designtokens.org |
| Animation Format | Linux Foundation LAC | lottie.github.io |
| Android Motion | Google M3 | m3.material.io |
| iOS Motion | Apple HIG | developer.apple.com/design |
| Windows Motion | Microsoft Fluent | fluent2.microsoft.design |
| Enterprise Motion | IBM Carbon | carbondesignsystem.com |
| Accessibility | W3C WCAG | w3.org/WAI/WCAG21 |

## Key Specifications

### W3C Design Tokens (2025.10)
- Stable specification for token interchange
- Supports: duration, cubicBezier, transition types
- Backed by: Adobe, Google, Microsoft, Figma, others
- URL: designtokens.org

### Lottie Spec v1.0 (2024)
- Vector animation interchange format
- IANA registered MIME type: video/lottie+json
- Maintained by: Linux Foundation Lottie Animation Community
- URL: lottie.github.io

### dotLottie v2.0
- Packaged Lottie container format
- Adds: theming, state machines, multi-animation
- Maintained by: LottieFiles
- URL: dotlottie.io/spec
