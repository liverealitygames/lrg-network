// Game list page JavaScript
// Handles filter toggling, form submission, and filter count badge

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('game-filter-form');
        const filterOpenInput = document.getElementById('filterOpenInput');
        const filtersContainer = document.getElementById('filtersContainer');
        const toggleBtn = document.getElementById('toggleFiltersBtn');

        if (!form || !filtersContainer || !toggleBtn) {
            return; // Required elements not found
        }

        // Initialize Bootstrap Select
        if (typeof $ !== 'undefined' && $.fn.selectpicker) {
            $('.selectpicker').selectpicker();

            // Handle Bootstrap Select change events for auto-submit
            // Bootstrap Select fires 'changed.bs.select' event, not regular 'change'
            $('.selectpicker').on('changed.bs.select', function() {
                // Don't auto-submit for country/region as they have special handling
                const id = $(this).attr('id');
                if (id !== 'country' && id !== 'region') {
                    submitFormWithNonEmptyParams();
                }
            });
        }

        // Helper to get URL param
        function getUrlParam(name) {
            const params = new URLSearchParams(window.location.search);
            return params.get(name);
        }

        // Helper to set/remove URL param without reloading
        function setUrlParam(name, value) {
            const url = new URL(window.location);
            if (value === null || value === undefined || value === '' || value === '0') {
                url.searchParams.delete(name);
            } else {
                url.searchParams.set(name, value);
            }
            window.history.replaceState({}, '', url);
        }

        // Filter count indicator logic
        function getFilterCount() {
            let count = 0;
            // Location: country, region, city (only count as 1 if any selected)
            const country = document.getElementById('country');
            const region = document.getElementById('region');
            const city = document.getElementById('city');
            if ((country && country.value) || (region && region.value) || (city && city.value)) {
                count += 1;
            }
            // Game format
            const gameFormat = document.getElementById('game_format');
            if (gameFormat && gameFormat.value) count += 1;
            // Game duration
            const gameDuration = document.getElementById('game_duration');
            if (gameDuration && gameDuration.value) count += 1;
            // Filming status
            const filmingStatus = document.getElementById('filming_status');
            if (filmingStatus && filmingStatus.value) count += 1;
            // Only active
            const inactiveFilter = document.getElementById('inactive_filter');
            if (inactiveFilter && inactiveFilter.value) count += 1;
            // College only
            const collegeFilter = document.getElementById('college_filter');
            if (collegeFilter && collegeFilter.value) count += 1;
            // For charity
            const charityFilter = document.getElementById('charity_filter');
            if (charityFilter && charityFilter.value) count += 1;
            // Friends and family only
            const friendsAndFamilyFilter = document.getElementById('friends_and_family_filter');
            if (friendsAndFamilyFilter && friendsAndFamilyFilter.value) count += 1;
            // Currently casting
            const castingFilter = document.getElementById('casting_filter');
            if (castingFilter && castingFilter.value) count += 1;
            return count;
        }

        function updateFilterCountBadge() {
            const badge = document.getElementById('filterCountBadge');
            if (!badge) return;
            const count = getFilterCount();
            if (count > 0) {
                badge.textContent = count;
                badge.classList.remove('hidden');
            } else {
                badge.textContent = '';
                badge.classList.add('hidden');
            }
        }

        // On page load, show/hide filters based only on filter_open param
        const filterOpen = getUrlParam('filter_open');
        if (filterOpen === '1') {
            filtersContainer.classList.remove('hidden');
            toggleBtn.setAttribute('aria-label', 'Hide Filters');
            toggleBtn.classList.add('active');
            if (filterOpenInput) filterOpenInput.value = '1';
        } else {
            filtersContainer.classList.add('hidden');
            toggleBtn.setAttribute('aria-label', 'Show Filters');
            toggleBtn.classList.remove('active');
            if (filterOpenInput) filterOpenInput.value = '0';
        }
        updateFilterCountBadge();

        // Toggle filter section and update URL param
        toggleBtn.addEventListener('click', function() {
            const isVisible = !filtersContainer.classList.contains('hidden');
            if (isVisible) {
                filtersContainer.classList.add('hidden');
                this.setAttribute('aria-label', 'Show Filters');
                this.classList.remove('active');
                setUrlParam('filter_open', '0');
                if (filterOpenInput) filterOpenInput.value = '0';
            } else {
                filtersContainer.classList.remove('hidden');
                this.setAttribute('aria-label', 'Hide Filters');
                this.classList.add('active');
                setUrlParam('filter_open', '1');
                if (filterOpenInput) filterOpenInput.value = '1';
            }
        });

        function submitFormWithNonEmptyParams() {
            const formData = new FormData(form);
            const params = new URLSearchParams();

            for (const [key, value] of formData.entries()) {
                if (value) {
                    params.append(key, value);
                }
            }
            // Always include filter_open if present
            if (filterOpenInput && filterOpenInput.value) {
                params.set('filter_open', filterOpenInput.value);
            }

            const queryString = params.toString();
            const action = form.getAttribute('action') || window.location.pathname;
            window.location.href = `${action}?${queryString}`;
        }

        // Expose function to global scope for inline onchange handlers
        window.submitFormWithNonEmptyParams = submitFormWithNonEmptyParams;

        // Update badge on any filter change
        const filterInputs = [
            'country', 'region', 'city', 'game_format', 'game_duration', 'filming_status',
            'inactive_filter', 'college_filter', 'charity_filter', 'friends_and_family_filter', 'casting_filter'
        ];
        filterInputs.forEach(function(id) {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', updateFilterCountBadge);
            }
        });

        const clearBtn = document.getElementById('clearSearch');
        const searchInput = document.getElementById('searchInput');

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (searchInput) searchInput.value = '';
                submitFormWithNonEmptyParams();
            });
        }

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            submitFormWithNonEmptyParams();
        });

        // Handle country change - reset region and city
        // Use Bootstrap Select event for country
        if (typeof $ !== 'undefined') {
            $('#country').on('changed.bs.select', function() {
                const regionSelect = document.getElementById('region');
                const citySelect = document.getElementById('city');

                // Reset and disable region and city dropdowns
                if (regionSelect) {
                    // Clear native select value first to prevent visual glitch
                    regionSelect.value = '';
                    $('#region').selectpicker('val', null);
                    $('#region').prop('disabled', false);
                    $('#region').selectpicker('refresh');
                }

                if (citySelect) {
                    // Clear native select value first to prevent visual glitch
                    citySelect.value = '';
                    $('#city').selectpicker('val', null);
                    $('#city').prop('disabled', true);
                    $('#city').selectpicker('refresh');
                }

                submitFormWithNonEmptyParams();
            });

            // Handle region change - reset city
            $('#region').on('changed.bs.select', function() {
                const citySelect = document.getElementById('city');

                // Reset and enable city dropdown
                if (citySelect) {
                    // Clear native select value first to prevent visual glitch
                    citySelect.value = '';
                    $('#city').selectpicker('val', null);
                    $('#city').prop('disabled', false);
                    $('#city').selectpicker('refresh');
                }

                submitFormWithNonEmptyParams();
            });
        }

        // Reset button
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                window.location.href = '/games/?filter_open=1';
            });
        }
    });
})();
