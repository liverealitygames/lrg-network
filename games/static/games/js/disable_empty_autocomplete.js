(function waitForDjangoJQuery() {
    if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
      setTimeout(waitForDjangoJQuery, 100);
      return;
    }

    (function($) {
      $(document).ready(function() {
        function toggleDisableAndReset($field, shouldDisable) {
          if (shouldDisable) {
            $field.prop('disabled', true).val(null).trigger('change.select2');
          } else {
            $field.prop('disabled', false).trigger('change.select2');
          }
        }

        function setupChainedDisabling() {
          var $country = $('#id_country');
          var $region = $('#id_region');
          var $city = $('#id_city');

          // Initial state
          toggleDisableAndReset($region, !$country.val());
          toggleDisableAndReset($city, !$region.val());

          $country.on('change select2:select', function() {
            $region.val(null).trigger('change.select2');  // reset region
            $city.val(null).trigger('change.select2');    // reset city
            toggleDisableAndReset($region, !$country.val());
            toggleDisableAndReset($city, true);
          });

          $region.on('change select2:select', function() {
            $city.val(null).trigger('change.select2');    // reset city
            toggleDisableAndReset($city, !$region.val());
          });
        }

        setupChainedDisabling();
      });
    })(django.jQuery);
  })();
