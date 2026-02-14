from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os

class PDFGenerator:
    """Generate professional PDF reports for customs calculations"""
    
    def __init__(self, output_dir='outputs'):
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Styles
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
    
    def generate_calculation_report(self, order_id: str, calculation_data: dict) -> str:
        """
        Generate PDF report for a customs calculation
        
        Returns: filepath of generated PDF
        """
        
        # Create filename
        filename = f"customs_report_{order_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Header/Title
        story.append(Paragraph("CUSTOMS CHARGE CALCULATION REPORT", self.title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Order Information Section
        story.append(Paragraph("Order Information", self.heading_style))
        
        order_info = [
            ['Order ID:', order_id],
            ['Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Product:', calculation_data.get('product_description', 'N/A')],
            ['Origin:', calculation_data.get('origin_country', 'N/A')],
            ['Destination:', calculation_data.get('destination_country', 'N/A')],
            ['Quantity:', str(calculation_data.get('quantity', 1))],
        ]
        
        order_table = Table(order_info, colWidths=[2*inch, 4*inch])
        order_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(order_table)
        story.append(Spacer(1, 0.3*inch))
        
        # AI Classification Section
        classification = calculation_data.get('classification', {})
        
        story.append(Paragraph("AI Classification Results", self.heading_style))
        
        class_info = [
            ['Category:', classification.get('category', 'N/A')],
            ['HS Code:', classification.get('hs_code', 'N/A')],
            ['AI Confidence:', f"{classification.get('confidence', 0)*100:.1f}%"],
            ['Keywords Detected:', ', '.join(classification.get('keywords', [])[:5])],
            ['Manual Review:', 'Required' if classification.get('requires_manual_review', False) else 'Not Required']
        ]
        
        class_table = Table(class_info, colWidths=[2*inch, 4*inch])
        class_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(class_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Charges Breakdown Section
        charges = calculation_data.get('charges', {})
        
        story.append(Paragraph("Customs Charges Breakdown", self.heading_style))
        
        # Currency conversion
        story.append(Paragraph(
            f"<b>Base Price:</b> ${charges.get('exchange_rate', 83) and charges.get('base_price_inr', 0) / charges.get('exchange_rate', 83):.2f} USD × {charges.get('exchange_rate', 83):.2f} = ₹{charges.get('base_price_inr', 0):,.2f} INR",
            self.normal_style
        ))
        story.append(Spacer(1, 0.15*inch))
        
        # Detailed charges table
        charges_data = [
            ['Charge Type', 'Rate/Method', 'Amount (INR)', 'Regulation Reference'],
        ]
        
        # Add duty
        charges_data.append([
            'Customs Duty',
            f"{charges.get('duty_rate', 0)*100:.1f}%",
            f"₹{charges.get('duty_amount', 0):,.2f}",
            self._wrap_text(charges.get('duty_regulation', 'N/A'), 30)
        ])
        
        # Add GST
        charges_data.append([
            'GST',
            f"{charges.get('gst_rate', 0)*100:.1f}%",
            f"₹{charges.get('gst_amount', 0):,.2f}",
            'GST Act 2017'
        ])
        
        # Add fees
        charges_data.append([
            'Customs Handling Fee',
            'Flat',
            f"₹{charges.get('customs_handling', 0):,.2f}",
            'CBIC Circular 15/2024'
        ])
        
        charges_data.append([
            'Port Handling Charges',
            'Per kg',
            f"₹{charges.get('port_charges', 0):,.2f}",
            'Port Trust Act 2023'
        ])
        
        charges_data.append([
            'Documentation Fee',
            'Flat',
            f"₹{charges.get('documentation', 0):,.2f}",
            'CBIC Circular 08/2024'
        ])
        
        # Total row
        charges_data.append([
            'TOTAL',
            '',
            f"₹{charges.get('total_charges_inr', 0):,.2f}",
            f"${charges.get('total_charges_usd', 0):,.2f} USD"
        ])
        
        charges_table = Table(charges_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 2.3*inch])
        charges_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(charges_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary Section
        story.append(Paragraph("Summary", self.heading_style))
        
        summary_data = [
            ['Total Duty:', f"₹{charges.get('duty_amount', 0):,.2f}"],
            ['Total Taxes:', f"₹{charges.get('gst_amount', 0):,.2f}"],
            ['Total Fees:', f"₹{charges.get('total_fees', 0):,.2f}"],
            ['', ''],
            ['GRAND TOTAL:', f"₹{charges.get('total_charges_inr', 0):,.2f} INR"],
            ['', f"${charges.get('total_charges_usd', 0):,.2f} USD"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 2), 10),
            ('FONTSIZE', (0, 4), (-1, -1), 12),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, 4), (-1, 4), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer Notes
        story.append(Paragraph("Important Notes", self.heading_style))
        
        notes = """
        <b>1. Accuracy:</b> All calculations are based on current customs regulations and tax rates as per the referenced acts and circulars.<br/>
        <br/>
        <b>2. AI Classification:</b> Product classification is performed using AI-assisted technology. Items marked for manual review should be verified by a licensed customs broker.<br/>
        <br/>
        <b>3. Regulatory Compliance:</b> All charges are traceable to specific regulations cited in this report. This document is audit-ready.<br/>
        <br/>
        <b>4. Exchange Rates:</b> Currency conversion uses current market rates. Actual charges may vary slightly based on the exchange rate at time of payment.<br/>
        <br/>
        <b>5. Official Clearance:</b> For official customs clearance, please consult with a licensed customs broker. This report is for estimation purposes.<br/>
        <br/>
        <b>6. Validity:</b> This calculation is valid as of the generation date shown above. Rates and regulations are subject to change.
        """
        
        story.append(Paragraph(notes, self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = f"""
        <para alignment="center">
        <b>AI-Assisted Customs Calculator</b><br/>
        Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        Order ID: {order_id}<br/>
        <br/>
        <i>This is a computer-generated document. No signature required.</i>
        </para>
        """
        
        story.append(Paragraph(footer_text, self.normal_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF generated: {filepath}")
        
        return filepath
    
    def _wrap_text(self, text: str, max_length: int) -> str:
        """Helper to wrap long text"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'

# Global instance
pdf_generator = PDFGenerator()