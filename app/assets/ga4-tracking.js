// Google Analytics 4 Event Tracking for Download Button
// This script tracks file downloads from the explorer tab with enhanced parameters
// including data type, date range, country, purpose, and user metadata

(function() {
    'use strict';
    
    // Function to send GA4 event
    function sendGA4Event(eventName, parameters) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, parameters);
            console.log('GA4 Event sent:', eventName, parameters);
        } else {
            console.warn('gtag not available, event not sent:', eventName, parameters);
            // Fallback: try to send to dataLayer directly
            if (window.dataLayer) {
                window.dataLayer.push({
                    'event': eventName,
                    ...parameters
                });
                console.log('Fallback: Event sent to dataLayer:', eventName, parameters);
            }
        }
    }
    
    // Function to get file details based on source
    function getFileDetails(source) {
        const fileDetails = {
            'emissions': {
                name: 'panama_canal_emissions_data',
                extension: 'csv',
                data_type: 'emissions',
                description: 'CO2 equivalent emissions data'
            },
            'waiting_time': {
                name: 'panama_canal_waiting_time_data',
                extension: 'csv',
                data_type: 'waiting_time',
                description: 'Vessel waiting time data'
            },
            'service_time': {
                name: 'panama_canal_service_time_data',
                extension: 'csv',
                data_type: 'service_time',
                description: 'Vessel service time data'
            },
            'energy': {
                name: 'panama_canal_energy_data',
                extension: 'csv',
                data_type: 'energy',
                description: 'Energy consumption data'
            }
        };
        
        return fileDetails[source] || {
            name: 'panama_canal_data',
            extension: 'csv',
            data_type: 'unknown',
            description: 'Panama Canal data'
        };
    }
    
    // Function to get date range information
    function getDateRangeInfo() {
        const sourceDropdown = document.querySelector('#explorer--source');
        const source = sourceDropdown ? sourceDropdown.value : 'unknown';
        
        let dateRange = '';
        let dateType = '';
        
        if (source === 'energy') {
            // For energy data, use week range
            const startWeek = document.querySelector('#explorer--start-week');
            const endWeek = document.querySelector('#explorer--end-week');
            const startWeekLabel = document.querySelector('#explorer--week-range-label');
            
            if (startWeek && endWeek && startWeekLabel) {
                dateRange = startWeekLabel.textContent || '';
                dateType = 'week_range';
            }
        } else {
            // For other data types, use month range
            const startDate = document.querySelector('#explorer--start-date');
            const endDate = document.querySelector('#explorer--end-date');
            const startDateLabel = document.querySelector('#explorer--range-label');
            
            if (startDate && endDate && startDateLabel) {
                dateRange = startDateLabel.textContent || '';
                dateType = 'month_range';
            }
        }
        
        return { dateRange, dateType };
    }
    
    // Function to get form information
    function getFormInfo() {
        const countryField = document.querySelector('#explorer--field-country');
        const purposeField = document.querySelector('#explorer--field-purpose');
        
        return {
            country: countryField ? countryField.value || '' : '',
            purpose: purposeField ? purposeField.value || '' : ''
        };
    }
    
    // Function to track download event
    function trackDownloadEvent(source) {
        const fileDetails = getFileDetails(source);
        const { dateRange, dateType } = getDateRangeInfo();
        const { country, purpose } = getFormInfo();
        
        // Get additional metadata
        const userAgent = navigator.userAgent;
        const language = navigator.language || 'unknown';
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'unknown';
        const screenResolution = `${screen.width}x${screen.height}`;
        
        const eventParameters = {
            file_name: fileDetails.name,
            file_extension: fileDetails.extension,
            download_source: 'explorer_tab',
            source_type: source || 'unknown',
            data_type: fileDetails.data_type,
            data_description: fileDetails.description,
            date_range: dateRange,
            date_type: dateType,
            country: country,
            purpose: purpose,
            content_type: 'csv_data',
            download_timestamp: new Date().toISOString(),
            user_language: language,
            user_timezone: timezone,
            screen_resolution: screenResolution,
            has_country_info: country ? 'yes' : 'no',
            has_purpose_info: purpose ? 'yes' : 'no',
            data_category: source === 'energy' ? 'energy_consumption' : 
                          source === 'emissions' ? 'environmental' : 
                          source === 'waiting_time' ? 'operational' : 
                          source === 'service_time' ? 'operational' : 'other',
            download_session_id: Date.now().toString(),
            page_url: window.location.href,
            referrer: document.referrer || 'direct'
        };
        
        sendGA4Event('file_download', eventParameters);
    }
    
    // Function to setup event listener
    function setupDownloadTracking() {
        // Use MutationObserver to watch for the download button being added to the DOM
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Check if the added node is the download button or contains it
                            const downloadButton = node.querySelector('#explorer--download-submit') || 
                                                  (node.id === 'explorer--download-submit' ? node : null);
                            
                            if (downloadButton && !downloadButton.hasAttribute('data-ga-tracked')) {
                                // Mark as tracked to prevent duplicate listeners
                                downloadButton.setAttribute('data-ga-tracked', 'true');
                                
                                // Add click event listener
                                downloadButton.addEventListener('click', function(e) {
                                    // Get the current source value from the dropdown
                                    const sourceDropdown = document.querySelector('#explorer--source');
                                    const source = sourceDropdown ? sourceDropdown.value : 'unknown';
                                    
                                    // Track the download event immediately on click
                                    trackDownloadEvent(source);
                                    
                                    // Let the original event continue
                                    // The download will proceed normally
                                });
                                
                                console.log('GA4 tracking setup for download button');
                            }
                        }
                    });
                }
            });
        });
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Also check if the button already exists (in case the script loads after the button)
        const existingButton = document.querySelector('#explorer--download-submit');
        if (existingButton && !existingButton.hasAttribute('data-ga-tracked')) {
            existingButton.setAttribute('data-ga-tracked', 'true');
            
            existingButton.addEventListener('click', function(e) {
                const sourceDropdown = document.querySelector('#explorer--source');
                const source = sourceDropdown ? sourceDropdown.value : 'unknown';
                trackDownloadEvent(source);
            });
            
            console.log('GA4 tracking setup for existing download button');
        }
        
        // Also watch for download component data changes as a backup
        const downloadComponent = document.querySelector('#explorer--download');
        if (downloadComponent) {
            const downloadObserver = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'data-dash-loading') {
                        // Download component is loading, which means a download was triggered
                        const sourceDropdown = document.querySelector('#explorer--source');
                        const source = sourceDropdown ? sourceDropdown.value : 'unknown';
                        trackDownloadEvent(source);
                    }
                });
            });
            
            downloadObserver.observe(downloadComponent, {
                attributes: true,
                attributeFilter: ['data-dash-loading']
            });
        }
    }
    
    // Initialize tracking when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupDownloadTracking);
    } else {
        setupDownloadTracking();
    }
    
    // Also setup when Dash finishes rendering (for dynamic content)
    document.addEventListener('dash:ready', setupDownloadTracking);
    
    // Fallback: setup after a short delay to catch any late-rendered elements
    setTimeout(setupDownloadTracking, 1000);
    
})();
