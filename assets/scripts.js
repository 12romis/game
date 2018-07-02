/**
 * Created by romis on 19.02.18.
 */


var current_img = $(this).attr('src');
var html = '<div class="wrapper">\
                        <p class="buscket-item">\
						<img id="new_img" class="new_img" src="'+current_img+'">\
					<span class="flex">\
						<span>\
							<p>Введите колличество:</p>\
							<input placeholder="01" type="text">\
						</span>\
						<span id="radio_block">\
							<p><input id="ampty" name="block" value="ampty" type="radio">Пустой блок</p>\
							<p><input id="polosa" name="block" value="polosa" type="radio">Блок в полоску</p>\
							<p><input id="kletka" name="block" value="kletka" type="radio">Блок в клетку</p>\
						</span>\
					</span>\
					<div class="button_zakaz">В КОРЗИНУ</div>\
				</div>';



$('.button_zakaz').click(function (e) {

    var img = $('.new_img').attr('src');
    var item_count = $('.item_count').val();
    var type =  $('input[name=block]:checked').val();

    var html = '<p>' +
        '<img src="'+img+'" alt="">' +
        'Количество: ' + item_count +
        'Тип: ' + type +
        '</p>';

    $('.bucket_container').append(html);
    alert('Добавлено в корзину');
});
