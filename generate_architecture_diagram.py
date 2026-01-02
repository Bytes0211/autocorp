#!/usr/bin/env python3
"""
Generate AutoCorp Data Lakehouse Architecture Diagram
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Canvas settings
WIDTH = 1920
HEIGHT = 1400
BACKGROUND = '#0f1419'
TEXT_COLOR = '#e6edf3'
ACCENT_COLOR = '#58a6ff'
SUCCESS_COLOR = '#3fb950'
WARNING_COLOR = '#d29922'
BOX_BG = '#161b22'
BORDER_COLOR = '#30363d'

def draw_rounded_rectangle(draw, xy, radius=10, fill=None, outline=None, width=2):
    """Draw a rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
    draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)
    if outline:
        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=width)
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=width)
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)

def draw_service_box(draw, x, y, width, height, title, details, color=ACCENT_COLOR, status=None):
    """Draw a service box with title and details"""
    draw_rounded_rectangle(draw, [x, y, x + width, y + height], 
                          radius=8, fill=BOX_BG, outline=color, width=2)
    
    # Title
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        font_title = ImageFont.load_default()
    
    draw.text((x + 10, y + 8), title, fill=color, font=font_title)
    
    # Details
    try:
        font_detail = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font_detail = ImageFont.load_default()
    
    y_offset = y + 35
    for detail in details:
        wrapped = textwrap.wrap(detail, width=28)
        for line in wrapped:
            draw.text((x + 10, y_offset), line, fill=TEXT_COLOR, font=font_detail)
            y_offset += 18
    
    # Status badge
    if status:
        badge_color = SUCCESS_COLOR if status == "✅" else WARNING_COLOR
        draw.text((x + width - 30, y + 8), status, fill=badge_color, font=font_title)

def draw_arrow(draw, x1, y1, x2, y2, color=ACCENT_COLOR, label=None):
    """Draw an arrow between two points"""
    draw.line([x1, y1, x2, y2], fill=color, width=3)
    
    # Arrow head
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    arrow_len = 15
    arrow_angle = math.pi / 6
    
    x3 = x2 - arrow_len * math.cos(angle - arrow_angle)
    y3 = y2 - arrow_len * math.sin(angle - arrow_angle)
    x4 = x2 - arrow_len * math.cos(angle + arrow_angle)
    y4 = y2 - arrow_len * math.sin(angle + arrow_angle)
    
    draw.polygon([x2, y2, x3, y3, x4, y4], fill=color)
    
    # Label
    if label:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except:
            font = ImageFont.load_default()
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        draw.text((mid_x + 5, mid_y - 15), label, fill=color, font=font)

# Create image
img = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND)
draw = ImageDraw.Draw(img)

# Title
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except:
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()

draw.text((60, 30), "AutoCorp Data Lakehouse", fill=TEXT_COLOR, font=font_title)
draw.text((60, 75), "Cloud-Native Data Engineering Platform | 50+ AWS Resources | 11 ETL Jobs", 
          fill=ACCENT_COLOR, font=font_subtitle)

# Layer 1: Data Sources (Top)
y_start = 130

# PostgreSQL
draw_service_box(draw, 80, y_start, 280, 140,
                "PostgreSQL Database",
                ["7 tables, 1.6M rows",
                 "• sales_order (397K)",
                 "• sales_order_parts (854K)",
                 "• customers, parts, services"],
                color=ACCENT_COLOR)

# CSV Files
draw_service_box(draw, 400, y_start, 280, 140,
                "CSV Test Data",
                ["792K orders + line items",
                 "• Intentional DQ issues",
                 "• Duplicate testing",
                 "• Missing/invalid data"],
                color=ACCENT_COLOR)

# Layer 2: Ingestion
y_ingestion = 310

# AWS DMS
draw_service_box(draw, 80, y_ingestion, 280, 120,
                "AWS DMS",
                ["CDC Replication",
                 "PostgreSQL → S3",
                 "Parquet output"],
                color=WARNING_COLOR, status="📝")

# AWS DataSync
draw_service_box(draw, 400, y_ingestion, 280, 120,
                "AWS DataSync",
                ["Large file transfers",
                 "CSV → S3 Raw",
                 "Scheduled sync"],
                color=WARNING_COLOR, status="📝")

# Layer 3: Data Lake (S3)
y_lake = 470
draw_service_box(draw, 730, y_start, 500, 400,
                "AWS S3 Data Lake",
                ["Zones:",
                 "• raw/database/ (DMS Parquet)",
                 "• raw/csv/ (CSV uploads)",
                 "• curated/ (Hudi tables)",
                 "• scripts/glue/ (PySpark)",
                 "• logs/",
                 "",
                 "Lifecycle Policies:",
                 "• Raw → Glacier (90d)",
                 "• Logs → Glacier (30d)"],
                color=SUCCESS_COLOR, status="✅")

# Layer 4: ETL & Processing
y_etl = 510

# AWS Glue
draw_service_box(draw, 80, y_etl, 280, 240,
                "AWS Glue",
                ["11 ETL Jobs (PySpark):",
                 "• 7 operational (COW/MOR)",
                 "• 3 analytics layer",
                 "• 1 CSV ingestion",
                 "",
                 "3 Crawlers:",
                 "• Schema discovery",
                 "• Data Catalog sync"],
                color=SUCCESS_COLOR, status="✅")

# Apache Hudi
draw_service_box(draw, 400, y_etl, 280, 240,
                "Apache Hudi",
                ["ACID transactions",
                 "Time-travel queries",
                 "COW: Read-optimized",
                 "MOR: Write-optimized",
                 "",
                 "Parquet + SNAPPY",
                 "Job bookmarking"],
                color=SUCCESS_COLOR, status="✅")

# Layer 5: Analytics & Query
y_analytics = 790

# AWS Athena
draw_service_box(draw, 80, y_analytics, 280, 140,
                "AWS Athena",
                ["Serverless SQL",
                 "5 named queries",
                 "Sub-30s queries",
                 "Presto engine"],
                color=SUCCESS_COLOR, status="✅")

# Analytics Layer
draw_service_box(draw, 400, y_analytics, 280, 140,
                "Analytics Layer",
                ["Denormalized tables:",
                 "• Sales fact",
                 "• Line items",
                 "• Service catalog"],
                color=SUCCESS_COLOR, status="✅")

# CloudWatch
draw_service_box(draw, 730, y_analytics, 240, 140,
                "CloudWatch",
                ["Dashboard (8 widgets)",
                 "3 Alarms:",
                 "• Glue failures",
                 "• Athena errors",
                 "• Cost threshold"],
                color=SUCCESS_COLOR, status="✅")

# IAM & Secrets
draw_service_box(draw, 1010, y_analytics, 220, 140,
                "IAM & Secrets",
                ["Least-privilege roles",
                 "Secrets Manager",
                 "Encryption at rest",
                 "TLS in transit"],
                color=SUCCESS_COLOR, status="✅")

# Infrastructure as Code
draw_service_box(draw, 1270, y_start, 300, 200,
                "Terraform IaC",
                ["98% Automated",
                 "8 modules deployed",
                 "50+ AWS resources",
                 "",
                 "Environments:",
                 "• dev.tfvars",
                 "• staging.tfvars",
                 "• prod.tfvars",
                 "",
                 "Remote state: S3"],
                color=SUCCESS_COLOR, status="✅")

# Future: AI Layer
draw_service_box(draw, 1270, y_analytics - 90, 300, 220,
                "Phase 5: AI Chatbox",
                ["Amazon Bedrock",
                 "Nova Pro LLM",
                 "RAG with OpenSearch",
                 "Query assistant",
                 "",
                 "Cost: +$150-180/mo"],
                color=WARNING_COLOR, status="📝")

# Draw arrows (data flow)
# PostgreSQL → DMS (center to center)
draw_arrow(draw, 220, y_start + 140, 220, y_ingestion, ACCENT_COLOR, "CDC")

# CSV → DataSync (center to center)
draw_arrow(draw, 540, y_start + 140, 540, y_ingestion, ACCENT_COLOR, "Upload")

# DMS → S3 (DMS right edge to S3 left edge)
draw_arrow(draw, 360, y_ingestion + 60, 730, y_start + 70, SUCCESS_COLOR, "Parquet")

# DataSync → S3 (DataSync right edge to S3 left edge)
draw_arrow(draw, 680, y_ingestion + 60, 730, y_start + 150, SUCCESS_COLOR, "CSV")

# S3 → Glue (S3 left edge to Glue top)
draw_arrow(draw, 780, y_start + 400, 220, y_etl, SUCCESS_COLOR, "Raw")

# Glue → Hudi (Glue right edge to Hudi left edge)
draw_arrow(draw, 360, y_etl + 120, 400, y_etl + 120, ACCENT_COLOR, "PySpark")

# Hudi → S3 (Hudi right edge to S3 left edge for curated zone)
draw_arrow(draw, 680, y_etl + 120, 730, y_start + 250, SUCCESS_COLOR, "Curated")

# S3 → Athena (S3 bottom to Athena top)
draw_arrow(draw, 850, y_start + 400, 220, y_analytics, SUCCESS_COLOR, "Query")

# Glue → Analytics Layer (Glue right bottom to Analytics top)
draw_arrow(draw, 320, y_etl + 240, 540, y_analytics, SUCCESS_COLOR, "ETL")

# Terraform → S3 (Terraform left to S3 right)
draw_arrow(draw, 1270, y_start + 100, 1230, y_start + 200, WARNING_COLOR, "IaC")

# Stats footer
y_footer = 980
try:
    font_footer = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
except:
    font_footer = ImageFont.load_default()

stats = [
    "Project Status: Phase 4 Complete (100% Core Pipeline)",
    "Data Volume: 1.6M PostgreSQL rows | 792K CSV test records",
    "Latency: <15 min end-to-end | <5 min CDC lag",
    "Cost: $50-80/mo (dev) | +$86-151/mo (with DMS)",
    "Legend: ✅ Deployed | 📝 Ready/Planned"
]

y_pos = y_footer
for stat in stats:
    draw.text((80, y_pos), stat, fill=TEXT_COLOR, font=font_footer)
    y_pos += 30

# Repository info
draw.text((80, HEIGHT - 60), "Repository: /home/scotton/dev/projects/autocorp", 
          fill=ACCENT_COLOR, font=font_footer)
draw.text((80, HEIGHT - 35), "Generated: 2025-12-31 | Co-Authored-By: Warp <agent@warp.dev>", 
          fill=BORDER_COLOR, font=font_footer)

# Save
output_path = '/home/scotton/dev/projects/autocorp/autocorp_architecture.png'
img.save(output_path, 'PNG')
print(f"Architecture diagram saved to: {output_path}")
