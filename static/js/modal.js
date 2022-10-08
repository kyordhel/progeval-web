function ModalObject(){
	this._emodal = document.getElementById('modal');;
	this._eheader = document.getElementById('modalheader');
	this._econtent = document.getElementById('modalcontent');
	this._efootyn = document.getElementById('modalfooter-yn');
	this._efootok = document.getElementById('modalfooter-ok');
	this._ebtnno = document.getElementById('modalbtn-no');
	this._ebtnyes = document.getElementById('modalbtn-yes');
	this._ebtnok = document.getElementById('modalbtn-ok');

	this.caption = null;
	this.text = null;
	this.buttons = null;
	this.onyes = null;
	this.onno = null;
	this.onok = null;

	this._ebtnno.addEventListener('click', function(){
		if(modal.onno) modal.onno();
		modal.hide();
	});
	this._ebtnyes.addEventListener('click', function(){
		if(modal.onyes) modal.onyes();
		modal.hide();
	});
	this._ebtnok.addEventListener('click', function(){
		if(modal.onok) modal.onok();
		modal.hide();
	});
}

ModalObject.prototype.clear = function() {
	this.caption = null;
	this.text = null;
	this.buttons = null;
	this._eheader.innerHTML = '';
	this._econtent.innerHTML = '';
	this.buttons = 'ok';
}

ModalObject.prototype.hide = function() {
	if (!this._efootyn.classList.contains('modal-hidden'))
		this._efootyn.classList.add('modal-hidden');
	if (!this._efootok.classList.contains('modal-hidden'))
		this._efootok.classList.add('modal-hidden');
	if (!this._emodal.classList.contains('modal-hidden'))
		this._emodal.classList.add('modal-hidden');
}

ModalObject.prototype.showyn = function() {
	this.buttons = 'yn';
	this.show();
}

ModalObject.prototype.showok = function() {
	this.buttons = 'ok';
	this.show();
}

ModalObject.prototype.show = function() {
	this._eheader.innerHTML = this.caption;
	this._econtent.innerHTML = this.text;
	if ((typeof this.buttons === 'string') || this.buttons instanceof String)
		this.buttons = this.buttons.toLowerCase();
	this.hide();

	switch (this.buttons){
		case 'yn':
			this._efootyn.classList.remove('modal-hidden');
			break;
		case 'ok':
		default:
			this._efootok.classList.remove('modal-hidden');
			break;
	}
	this._emodal.classList.remove('modal-hidden');
}

modal = null;
window.onload = function(){
	modal = new ModalObject();
	// modal.show();
}


function addClass(elementId, className){
	e = document.getElementById(elementId);
	if(e && e.classList.contains(className))
		e.classList.add(className)
}

function removeClass(elementId, className){
	e = document.getElementById(elementId);
	console.log(e);
	if(!e || !e.classList.contains(className))
		return;
	e.classList.remove(className)
}

function showmodal(caption, text, buttons){
	document.getElementById('modalheader').innerHTML = caption;
	document.getElementById('modalcontent').innerHTML = text;
	if ((typeof buttons === 'string') || buttons instanceof String)
		buttons = buttons.toLowerCase();

	addClass('modalfooter-yn', 'modal-hidden');
	addClass('modalfooter-ok', 'modal-hidden');

	switch (buttons){
		case 'yn':
			removeClass('modalfooter-yn', 'modal-hidden');
			break;
		case 'ok':
			removeClass('modalfooter-ok', 'modal-hidden');
			break;
		default:
			removeClass('modalfooter-ok', 'modal-hidden');
			break;
	}
	removeClass('modal', 'modal-hidden');
}

function hidemodal(){
	document.getElementById('modalheader').innerHTML = '';
	document.getElementById('modalcontent').innerHTML = '';
	addClass('modalfooter-yn', 'modal-hidden');
	addClass('modalfooter-ok', 'modal-hidden');
	addClass('modal', 'modal-hidden');
}
