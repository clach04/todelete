# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#

import os
import random
import json

from django.conf import settings
from django.views.generic import FormView, TemplateView
from django.core.urlresolvers import reverse
from forms import PlayerForm

import scripts  # FIXME name

# FIXME prototype models, mostly using dict whilst
# we work out what the model/objects look like
filename = os.path.join(scripts.data_dir, 'data.json')
with open(filename, 'rb') as f:
    # game is one game, hard coded ;-)
    game = json.loads(f.read())

game['white_deck'] = range(len(game['white_cards']))
game['black_deck'] = range(len(game['black_cards']))
"""Shuffle deck, uses built in random, it may be better to plugin a better
random init routine and/also consider using
https://pypi.python.org/pypi/shuffle/

Also take a look at http://code.google.com/p/gcge/
"""
random.shuffle(game['white_deck'])
random.shuffle(game['black_deck'])

game['players'] = []

player_white_cards = []
for _ in range(10):
    player_white_cards.append(game['white_deck'].pop())
game['players'].append({'player_white_cards': player_white_cards, 'name': 'Philip', 'wins': 0,})
game['card_czar'] = 0

class PlayerView(FormView):

    template_name = 'player.html'
    form_class = PlayerForm

    def __init__(self, *args, **kwargs):
        self.read_player()
        super(PlayerView, self).__init__(*args, **kwargs)


    def get_success_url(self):
        return reverse('player-view')

    def get_context_data(self, **kwargs):
        # FIXME relationship between this and read_player()
        context = super(PlayerView, self).get_context_data(**kwargs)
        self.request.session['player_name'] = self.player['name']
        context['name_from_session'] = self.request.session.get('player_name', '')
        player_number = 0  # FIXME get this from session
        self.is_card_czar = context['is_card_czar'] = game['card_czar'] == player_number
        hand = []
        player_hand = game['players'][player_number]['player_white_cards']
        for card_num in player_hand:
            hand.append((card_num, game['white_cards'][card_num]))
        context['cards'] = hand
        self.player['hand'] = hand
        context['player_name'] = self.player['name']
        context['selected'] = self.player['selected']
        return context

    def get_form_kwargs(self):
        kwargs = super(PlayerView, self).get_form_kwargs()
        kwargs['cards'] = tuple(tuple(card) for card in self.player['hand'])
        return kwargs

    def form_valid(self, form):
        self.player['selected'] = form.cleaned_data['card_selection']
        self.write_player()
        print form.cleaned_data['card_selection']
        return super(PlayerView, self).form_valid(form)

    def read_player(self):
        player_number = 0  # FIXME get this from session
        self.player = game['players'][player_number]
        hand = []
        player_hand = game['players'][player_number]['player_white_cards']
        for card_num in player_hand:
            hand.append((card_num, game['white_cards'][card_num]))
        self.player['hand'] = hand
        self.player['selected'] = ''  # what is this?

    def write_player(self):
        pass  # FIXME delete or db IO?

class GameView(FormView):

    template_name = 'player.html'
    form_class = PlayerForm

    # def get_form_kwargs


class LobbyView(TemplateView):

    template_name = 'lobby.html'
