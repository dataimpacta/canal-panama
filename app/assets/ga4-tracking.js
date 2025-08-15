// Google Analytics 4 Event Tracking for Download Button
// This script tracks file downloads from the explorer tab

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
                extension: 'csv'
            },
            'waiting_time': {
                name: 'panama_canal_waiting_time_data',
                extension: 'csv'
            },
            'service_time': {
                name: 'panama_canal_service_time_data',
                extension: 'csv'
            },
            'energy': {
                name: 'panama_canal_energy_data',
                extension: 'csv'
            }
        };
        
        return fileDetails[source] || {
            name: 'panama_canal_data',
            extension: 'csv'
        };
    }
    
    // Function to track download event
    function trackDownloadEvent(source) {
        const fileDetails = getFileDetails(source);
        
        const eventParameters = {
            file_name: fileDetails.name,
            file_extension: fileDetails.extension,
            download_source: 'explorer_tab',
            source_type: source || 'unknown'
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
