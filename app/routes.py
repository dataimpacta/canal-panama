"""Additional routes for the Panama Canal Analytics app."""

from flask import Response


def register_routes(app):
    """Register additional routes with the Flask app."""
    
    @app.server.route("/privacy")
    def privacy():
        """Serve the privacy notice page."""
        html_doc = """
        <html>
        <head>
            <title>Privacy Notice – Panama Canal Analytics</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 760px;
                    margin: 0 auto;
                    padding: 24px;
                    background-color: #f8f9fa;
                }
                .container {
                    background: white;
                    padding: 32px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #007bff;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 8px;
                }
                h2 {
                    color: #495057;
                    margin-top: 24px;
                }
                ul {
                    padding-left: 20px;
                }
                li {
                    margin-bottom: 8px;
                }
                .back-link {
                    display: inline-block;
                    margin-top: 24px;
                    color: #007bff;
                    text-decoration: none;
                    font-weight: 500;
                }
                .back-link:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Privacy Notice – Panama Canal Analytics</h1>
                
                <p><strong>Controller:</strong>  Panama Canal Analytics Team</p>
                <p><strong>Contact:</strong> gabriel.fuentes@nhh.no</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
                
                <h2>1. What we collect</h2>
                <p>When you download data from our platform, we collect the following information:</p>
                <ul>
                    <li>Country (as provided in the form)</li>
                    <li>Purpose of the download (as provided in the form)</li>
                    <li>Email address (if you choose to provide it; immediately hashed, see below)</li>
                </ul>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
                
                <h2>2. How we process your email</h2>
                <ul>
                    <li>Your email is immediately converted into a secure one-way hash (SHA-256).</li>
                    <li>We never store or use your actual email.</li>
                    <li>The hash cannot be reversed into your original email, but it allows us to:</li>
                    <ul>
                        <li>Track unique downloads</li>
                        <li>Deduplicate repeated requests</li>
                        <li>Generate anonymised statistics</li>
                    </ul>
                </ul>
                <p>Your email (or its hash) is never used for marketing, sales, or third-party sharing.</p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
                
                <h2>3. Purpose of processing</h2>
                <p>We process your data to:</p>
                <ul>
                    <li>Understand usage by region and purpose</li>
                    <li>Generate anonymised statistics to improve our platform</li>
                    <li>Track unique users while avoiding storage of personal identifiers</li>
                </ul>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
                
                <h2>4. Legal basis</h2>
                <p>We rely on your consent (GDPR Art. 6(1)(a)) for collecting and processing your email for analytics purposes.</p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
                
                <h2>5. Retention</h2>
                <p>We retain data only as long as necessary to fulfil the purposes described in this notice.</p>
                <p>We periodically review our datasets and delete records that are no longer required.</p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
                
                <h2>6. Sharing and transfers</h2>
                <ul>
                    <li>We may use trusted service providers (e.g. cloud hosting, storage) under strict data processing agreements.</li>
                    <li>We do not sell or share your data with third parties.</li>
                    <li>Where data is transferred outside the EEA, we rely on Standard Contractual Clauses to safeguard your rights.</li>
                </ul>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
                
                <h2>7. Your rights</h2>
                <p>Under GDPR and applicable U.S. data protection laws, you have the right to:</p>
                <ul>
                    <li>Access, correct, or delete your data</li>
                    <li>Restrict or object to processing</li>
                    <li>Withdraw your consent at any time (by contacting us)</li>
                    <li>Request portability of your data in certain circumstances</li>
                    <li>Lodge a complaint with your local data protection authority</li>
                </ul>
                
                <a href="/explorer" class="back-link">← Back to Dashboard</a>
            </div>
        </body>
        </html>
        """
        return html_doc

    @app.server.route("/download-data-dictionary")
    def download_data_dictionary():
        """Serve the data dictionary as a text file."""
        data_dictionary = """
PANAMA CANAL ANALYTICS - DATA DICTIONARY
========================================

This document provides detailed information about the data sources and variables available in the Panama Canal Analytics dashboard.

DATA SOURCES
===========

1. EMISSIONS DATA
-----------------
Source: Maritime vessel emissions data from Panama Canal operations
Description: CO2 equivalent emissions data aggregated by vessel type, location, and time period

Variables:
- Year: Calendar year of the emission measurement
- Month: Calendar month (1-12) of the emission measurement  
- Resolution Id: H3 geospatial index identifier for location-based aggregation
- StandardVesselType: Standardized classification of vessel type (e.g., Container, Oil tanker, Bulk Carrier)
- Co2 Equivalent T: Total CO2 equivalent emissions in tonnes
- Year Month: Combined year-month identifier in YYYYMM format (e.g., 202301 for January 2023)

2. WAITING AND SERVICE TIME DATA
--------------------
Source: Panama Canal vessel transit and waiting time records
Description: Vessel waiting times and service times at different canal locations and stop areas

Variables:
- Year: Calendar year of the time measurement
- Month: Calendar month (1-12) of the time measurement
- StandardVesselType: Standardized classification of vessel type
- Stop Area: Specific location or area where vessels wait (e.g., PPC Balboa, MIT, Panama Canal South Transit)
- Service Time: Time in hours that vessels spend in active service/transit
- Waiting Time: Time in hours that vessels spend waiting before service
- Sample Size: Number of vessels included in the aggregated measurement
- Neo Transit: Indicator for new/neo vessel transit classification
- Year Month: Combined year-month identifier in YYYYMM format

3. ENERGY DATA
--------------
Source: Energy demand data for maritime operations in Panama Canal region
Description: Energy consumption data aggregated by origin/destination countries and time periods

Variables:
- Year: Calendar year of the energy measurement
- Week: ISO week number (1-53) of the energy measurement
- Country Before: ISO-2 country code for origin country
- Country After: ISO-2 country code for destination country
- Sum Energy: Total energy consumption in kilowatt-hours (kWh) between two nodes
- Year Week: Combined year-week identifier in YYYYWW format (e.g., 202301 for week 1 of 2023)
- Year Month: Combined year-month identifier derived from year-week
- Country Before Name: Full country name for origin country
- Country After Name: Full country name for destination country

DATA QUALITY NOTES
=================
- All time-based variables use consistent date formatting (YYYYMM for months, YYYYWW for weeks)
- Vessel types follow standardized maritime classification system
- Geographic data uses H3 hexagonal grid system for spatial aggregation
- Energy data includes both origin and destination country information for route analysis
- Sample sizes are provided for waiting/service time data to indicate data reliability

"""
        
        return Response(
            data_dictionary,
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment; filename=data_dictionary.txt'}
        )
