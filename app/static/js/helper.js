(function ($) {
    $(document).ready(function() {
        $('.js-simple-select').select2();
        $('.js-select-copie-tags').select2({multiple: true, tags: "true"});

        $('.js-select-correspondant-ajax').select2({
            ajax:{
                url:'/_search_correspondent',
                dataType: 'json',
                data: function(params){
                    return{
                        q: params.term,
                    };
                },
                processResults: function(data, params){
                    console.log(data);
                    return {
                        results: $.map(data, function (item) {
                            return {
                                text: item.nom,
                                id: item.nom
                            }
                        })
                    };
                },
                cache: true
            }
        });

        $('.js-select-reference-ajax').select2({
            ajax:{
                url:'/_search_reference',
                dataType: 'json',
                data: function(params){
                    return{
                        q: params.term,
                    };
                },
                processResults: function(data, params){
                    console.log(data);
                    return {
                        results: $.map(data, function (item) {
                            return {
                                text: item.reference,
                                id: item.reference
                            }
                        })
                    };
                },
                cache: true
            }
        });
    })
})(jQuery);