"""
Simple Markdown to PDF converter using md2pdf
"""

from md2pdf.core import md2pdf
from pathlib import Path

# Paths
artifact_dir = Path(r'C:\Users\BALASARAVANAN\.gemini\antigravity\brain\35b59cfd-9bbb-44e2-bee7-4ceaa8eb2cdf')
output_dir = Path(r'd:\Project_8th\backend')

# Convert walkthrough
walkthrough_md = artifact_dir / 'walkthrough.md'
walkthrough_pdf = output_dir / '8Phase_Walkthrough.pdf'

print("🔄 Converting walkthrough.md to PDF...")
print(f"   Input: {walkthrough_md}")
print(f"   Output: {walkthrough_pdf}")

try:
    md2pdf(
        str(walkthrough_pdf),
        md_file_path=str(walkthrough_md),
        base_url=str(artifact_dir)
    )
    print("✅ Walkthrough PDF created successfully!")
    print(f"   📄 {walkthrough_pdf}")
except Exception as e:
    print(f"❌ Error: {e}")

# Also convert README as bonus
readme_md = output_dir / '8PHASE_README.md'
readme_pdf = output_dir / '8Phase_QuickReference.pdf'

if readme_md.exists():
    print("\n🔄 Converting 8PHASE_README.md to PDF...")
    try:
        md2pdf(
            str(readme_pdf),
            md_file_path=str(readme_md),
            base_url=str(output_dir)
        )
        print("✅ Quick Reference PDF created successfully!")
        print(f"   📄 {readme_pdf}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n✅ PDF generation complete!")
