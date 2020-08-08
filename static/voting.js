// Details of page
var can = true;
var award_ids = [];
var num_of_awards = 0;
window.addEventListener('load', function () {
    var cards = document.getElementsByName('navbar_buttons');
    Array.prototype.filter.call(cards, function(card) {
        award_ids.push(card.getAttribute('data-award-id'));
    });
    num_of_awards = award_ids.length;
});
        

// To open different awards
function next(award)
{
    document.getElementsByClassName('card')[0].classList.add('collapse');
    document.getElementById('award_button_for_' + award).classList.add('collapse.show');
}

// While form submission
window.addEventListener('load', function() {
    document.getElementById('form_submit').addEventListener('submit', function (event) {
        event.preventDefault();
        event.stopPropagation();
        var votes = document.getElementsByClassName('custom-control-input');
        Array.prototype.filter.call(votes, function (vote) {
            if (vote.checked)
            {
                var award = vote.getAttribute('data-award-id');
                var id = vote.getAttribute("data-nominee-id");
                document.getElementById(award).value = id;
            }
            
            demo.innerHTML = vote.getAttribute("data-nominee-id");
        });
        document.getElementById('form_submit').submit();
    });
});

// To get the name in options
window.addEventListener('load', function naming () {
    // Fetching all the options
    var labels = document.getElementsByName('labels');

    // Looping over them
    Array.prototype.filter.call(labels, function (label) {
        var id = label.getAttribute("data-nominee-id");
        var award_id = label.getAttribute("data-award-id");
        if (id) {
            $.get("/name_and_pic?answer=" + id, function(data) {
                document.getElementById('name_var_for_label_of_' + id + '_and_' + award_id).innerHTML = data[0];
                document.getElementById('img_for_label_of_' + id + '_and_' + award_id).setAttribute('src', data[1]);
            });
        }
    });
});
        

// To confirm the css of buttons
window.addEventListener('load', function() {
    award_ids.some(function(award_id) {
        options = document.getElementsByName('nominee_options_for_' + award_id);
        Array.prototype.filter.call(options, function(option) {
            if (option.checked)
            {
                btn = document.getElementById('navbar_award_button_for_' + award_id);
                btn.classList.remove('btn-secondary');
                btn.classList.add('btn-success');
            }
        });
    });
});

function ch(award) {
    document.getElementById('or_' + award).checked = true;
}

// To handle the css while checking options
function option_check (nominee_id, award_id, or_for) {
    options = document.getElementsByName('nominee_options_for_' + award_id);
    if (options.length > 1)
    {
        Array.prototype.filter.call(options, function(option) {
            if (option.getAttribute('data-main-option') === "true")
            {
                div = document.getElementById('div_for_' + option.getAttribute('data-nominee-id') + '_of_' + award_id);
            }
            else
            {
                div = document.getElementById('div_for_' + option.getAttribute('data-award-id'));
            }
            div.classList.remove('btn-info');
            div.classList.add('btn-outline-info');
        });
    }
    if (or_for)
    {
        ch(award_id);
        div2 = document.getElementById('div_for_' + award_id);
    }
    else
    {
        document.getElementById(nominee_id + '&' + award_id).checked = true;
        div2 = document.getElementById('div_for_' + nominee_id + '_of_' + award_id);
    }
    div2.classList.remove('btn-outline-info');
    div2.classList.add('btn-info');
    btn = document.getElementById('navbar_award_button_for_' + award_id);
    btn.classList.remove('btn-secondary');
    btn.classList.add('btn-success');
}

// To submit an alternative nominee
function search(award)
{
    input = document.getElementById('answer_for_' + award);
    $.get('/search?answer=' + input.value, function (data) {
            document.getElementById('options_for_' + award).innerHTML = data;
        });
    setTimeout(() => {
        change(award);            
    }, 100);    
}

// For options
function change (award)
{
    var id = 0;
    preset_options = document.getElementsByName('nominee_options_for_' + award);
    var option = document.getElementById('options_for_' + award).options[0];
    if (!option)
    {
        return true;
    }
    var option2 = document.getElementById('options_for_' + award).options[1];
    var input = document.getElementById('answer_for_' + award);
    if (input.value.toUpperCase() === option.value.toUpperCase() || !option2)
    {
        id = option.getAttribute('data-nominee-id');
        Array.prototype.filter.call(preset_options, function (preset_option) {
            preset_option_id = preset_option.getAttribute('data-nominee-id');
            if (preset_option_id == id && document.getElementById('or_' + award).getAttribute('data-nominee-id') != id)
            {
                option_check(preset_option_id, award, 0);
                can = false;
                input.value = '';
                input.blur();
                return false;
            }
        });
        if (can)
        {
            document.getElementById('input_for_' + award).style.display="none";
            document.getElementById('or_for_' + award).style.display="";
            document.getElementById('or_' + award).setAttribute("data-nominee-id", id);
            $.get("/name_and_pic?answer=" + id, function(data) {
                $('#name_var_for_label_of_' + award).text(data[0]);
                $('#img_for_or_for_' + award).attr({src : data[1]});
            });
            option_check(id, award, 1);
        }
        btn = document.getElementById('navbar_award_button_for_' + award);
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-success');
    }
}

// To clear choices
function reload_content(award) {
    can = true;
    var options = document.getElementsByName('nominee_options_for_' + award);
    Array.prototype.filter.call(options, function(option) {
        option.checked = false;
        if (option.getAttribute('data-main-option') === "true")
        {
            div = document.getElementById('div_for_' + option.getAttribute('data-nominee-id') + '_of_' + award);
        }
        else
        {
            div = document.getElementById('div_for_' + option.getAttribute('data-award-id'));
        }
        div.classList.remove('btn-info');
        div.classList.add('btn-outline-info');
    });
    document.getElementById('answer_for_' + award).value = '';
    document.getElementById('input_for_' + award).style.display="";
    document.getElementById('or_for_' + award).style.display="none";
    btn = document.getElementById('navbar_award_button_for_' + award);
    btn.classList.add('btn-secondary');
    btn.classList.remove('btn-success');
}

// Showing the first unvoted award at the start
window.addEventListener('load', function(){
    first_award = true;
    award_ids.some(function (award) {
        card = document.getElementById('card_for_' + award);
        btn = document.getElementById('display_button_for_' + award);
        options = document.getElementsByName('nominee_options_for_' + award);
        if (!options || !options[0].checked)
        {
            card.classList.remove('collapse');
            card.classList.add('collapse.show');
            btn.classList.add('active');
            first_award = false;
            return true;
        }   
    });
    if (first_award)
    {
        document.getElementById('card_for_' + award_ids[0]).classList.remove('collapse');
        document.getElementById('card_for_' + award_ids[0]).classList.add('collapse.show');
        document.getElementById('display_button_for_' + award_ids[0]).classList.add('active');
    }
});

// To display a particular award
function display(award) {
    // Hiding current card
    card = document.getElementsByClassName('collapse.show')[0];
    btn = document.getElementsByClassName('active')[0];
    btn.classList.remove('active');
    card.classList.remove('collapse.show');
    card.classList.add('collapse');

    // Displaying next card
    next_card = document.getElementById('card_for_' + award);
    next_btn = document.getElementById('display_button_for_' + award);
    next_card.classList.remove('collapse');
    next_card.classList.add('collapse.show');
    next_btn.classList.add('active');

    // Special Case
    if (next_card.getAttribute('data-award-id') === award_ids[num_of_awards - 1])
    {
        document.getElementById('next_btn').style.display="none";
        document.getElementById('card_submit_btn').style.display="";
    }

    //CHOICE
    /*else
    {
        document.getElementById('next_btn').style.display="";
        document.getElementById('form_submit').style.display="none";
    }*/
};

// To display next award
function next() {
    card = document.getElementsByClassName('collapse.show')[0];
    award_id = card.getAttribute('data-award-id');
    if (award_id === award_ids[num_of_awards - 1])
    {
        document.getElementById('submit_btn').click();
    }
    else
    {
        display(award_ids[award_ids.indexOf(award_id) + 1]);
    }
}

// To display previous award
function back() {
    card = document.getElementsByClassName('collapse.show')[0];
    award_id = card.getAttribute('data-award-id');
    if (award_id === award_ids[0])
    {
        display(award_ids[num_of_awards - 1]);
    }
    else
    {
        display(award_ids[award_ids.indexOf(award_id) - 1]);
    }
}

// To deal with enterkey
document.addEventListener('keydown', (event) => {if (event.keyCode == 13) next()});
function card_submit_button() {
    document.getElementById('submit_btn').click();
}