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
                description: 'CO2 equivalent emissions data',
                display_name: 'Emissions'
            },
            'waiting_time': {
                name: 'panama_canal_waiting_time_data',
                extension: 'csv',
                data_type: 'waiting_time',
                description: 'Vessel waiting time data',
                display_name: 'Waiting Time'
            },
            'service_time': {
                name: 'panama_canal_service_time_data',
                extension: 'csv',
                data_type: 'service_time',
                description: 'Vessel service time data',
                display_name: 'Service Time'
            },
            'energy': {
                name: 'panama_canal_energy_data',
                extension: 'csv',
                data_type: 'energy',
                description: 'Energy consumption data',
                display_name: 'Energy'
            }
        };
        
        return fileDetails[source] || {
            name: 'panama_canal_data',
            extension: 'csv',
            data_type: 'unknown',
            description: 'Panama Canal data',
            display_name: 'Unknown'
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
        // Debug: Log the source value being received
        console.log('GA4 Debug - Source value received:', source);
        
        // If source is unknown or empty, try to get from the dropdown
        if (!source || source === 'unknown') {
            const sourceDropdown = document.querySelector('#explorer--source');
            if (sourceDropdown) {
                // Try to get the value
                if (sourceDropdown.value) {
                    source = sourceDropdown.value;
                    console.log('GA4 Debug - Got source from dropdown value:', source);
                }
                // If no value, try to get from selected option
                else if (sourceDropdown.options && sourceDropdown.selectedIndex >= 0) {
                    source = sourceDropdown.options[sourceDropdown.selectedIndex].value;
                    console.log('GA4 Debug - Got source from dropdown selected option:', source);
                }
                // If still no value, try to get from the visible text
                else {
                    const selectedText = sourceDropdown.options[sourceDropdown.selectedIndex]?.text || '';
                    console.log('GA4 Debug - Dropdown selected text:', selectedText);
                    // Map the display text back to the source value
                    if (selectedText.toLowerCase().includes('emissions')) {
                        source = 'emissions';
                    } else if (selectedText.toLowerCase().includes('waiting')) {
                        source = 'waiting_time';
                    } else if (selectedText.toLowerCase().includes('service')) {
                        source = 'service_time';
                    } else if (selectedText.toLowerCase().includes('energy')) {
                        source = 'energy';
                    }
                    console.log('GA4 Debug - Mapped source from text:', source);
                }
            }
        }
        
        const fileDetails = getFileDetails(source);
        console.log('GA4 Debug - File details name:', fileDetails.name);
        
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
            source_display_name: fileDetails.display_name,
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
                                    // Use a small delay to ensure dropdown is properly initialized
                                    setTimeout(function() {
                                        // Get the current source value from the dropdown
                                        const sourceDropdown = document.querySelector('#explorer--source');
                                        console.log('GA4 Debug - Dropdown element found:', !!sourceDropdown);
                                        console.log('GA4 Debug - Dropdown value:', sourceDropdown ? sourceDropdown.value : 'no dropdown');
                                        
                                        let source = 'unknown';
                                        if (sourceDropdown) {
                                            source = sourceDropdown.value;
                                        }
                                        
                                        // Track the download event
                                        trackDownloadEvent(source);
                                    }, 100);
                                    
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
                setTimeout(function() {
                    const sourceDropdown = document.querySelector('#explorer--source');
                    let source = 'unknown';
                    if (sourceDropdown) {
                        source = sourceDropdown.value;
                    }
                    trackDownloadEvent(source);
                }, 100);
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
