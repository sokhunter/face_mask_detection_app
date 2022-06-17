$(function () {
    var $dateRangePicker = $('#date-range-picker');
    document.getElementById('start-date').value = $dateRangePicker.data("start-date");
    document.getElementById('end-date').value = $dateRangePicker.data("end-date");
    $('#date-range-picker').daterangepicker({
        "autoApply": true,
        "locale": {
            "format": "DD/MM/YYYY",
            "separator": " - ",
            "applyLabel": "Aceptar",
            "cancelLabel": "Cancelar",
            "fromLabel": "Desde",
            "toLabel": "Hasta",
            "customRangeLabel": "Custom",
            "weekLabel": "S",
            "daysOfWeek": [
                "Do",
                "Lu",
                "Ma",
                "Mi",
                "Ji",
                "Vi",
                "Sa"
            ],
            "monthNames": [
                "Enero",
                "Febrero",
                "Marzo",
                "Abril",
                "Mayo",
                "Junio",
                "Julio",
                "Agosto",
                "Septiembre",
                "Octubre",
                "Noviembre",
                "Diciembre"
            ],
            "firstDay": 1
        },
        "linkedCalendars": false,
        "startDate": moment($dateRangePicker.data("start-date"), "DD/MM/YYYY"),
        "endDate": moment($dateRangePicker.data("end-date"), "DD/MM/YYYY"),
        "maxDate": moment($dateRangePicker.data("max-date"), "DD/MM/YYYY"),
        "buttonClasses": "btn btn-sm",
        "applyButtonClasses": "btn-primary",
        "cancelClass": "btn-default"
    }, function(start, end, label) {
        document.getElementById('start-date').value = start.format('DD/MM/YYYY')
        document.getElementById('end-date').value = end.format('DD/MM/YYYY')
    });

    Inputmask('datetime', {'inputFormat': 'HH:MM'}).mask($(".timePicker"));
});
