# This file is part of the CERN Indico plugins.
# Copyright (C) 2014 - 2020 CERN
#
# The CERN Indico plugins are free software; you can redistribute
# them and/or modify them under the terms of the MIT License; see
# the LICENSE file for more details.

from __future__ import unicode_literals

import json
import os
import re
from datetime import datetime, time

from flask import current_app, redirect, request, session, url_for
from marshmallow import ValidationError, fields
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired
from wtforms.widgets.core import TextArea

from indico.core import signals
from indico.core.db import db
from indico.core.errors import NoReportError
from indico.core.plugins import IndicoPlugin
from indico.modules.rb.models.reservations import Reservation
from indico.modules.rb.models.rooms import Room
from indico.web.forms.base import IndicoForm
from indico.web.util import ExpectedError

from . import _
from .blueprint import blueprint


class SettingsForm(IndicoForm):
    split_room_config = StringField(_('Split room config'), [DataRequired()],
                          description=_('JSON array for split rooms'))


class SplitRoomPlugin(IndicoPlugin):
    """SplitRoom

    Automatically create bookings for split rooms
    """
    configurable = True
    settings_form = SettingsForm
    default_settings = {
        'split_room_config': '',
    }

    def init(self):
        super(SplitRoomPlugin, self).init()

        #        #Executed after a booking has been cancelled/rejected/accepted. The *sender*
        #is the `Reservation` object.
        self.connect(signals.rb.booking_created, self.onBookingCreated)

        #Executed after a booking has been cancelled/rejected/accepted. The *sender*
        #is the `Reservation` object.
        #self.connect(signals.rb.booking_state_changed, self.onBookingStateChanged)

        #Executed after a booking has been deleted. The *sender* is the `Reservation` object.
        #self.connect(signals.rb.booking_deleted, self.onBookingDeleted)

        #Executed after the state of a booking occurrence changed.
        #The *sender* is the `ReservationOccurrence` object.
        self.connect(signals.rb.booking_occurrence_state_changed, self.onOccurencesChanged)

    def get_blueprints(self):
        yield blueprint

    @property
    def splitmap(self):
        data = json.loads(SplitRoomPlugin.settings.get('split_room_config'))
        return { int(k): v for k,v in data.items()}

    def _checkSplitRooms(self, room, occs):

        if room in self.splitmap:
            for ri in self.splitmap[room]:
                oroom = Room.get_or_404(ri, is_deleted=False)
                overlap = Reservation.find_overlapping_with(oroom,occs).all()
                if overlap:
                    raise ExpectedError('Overlaps with other reservations in {}.'.format(oroom.name))

        else:
            for ri, splits in self.splitmap.items():
                if room in splits:
                    oroom = Room.get_or_404(ri, is_deleted=False)
                    overlap = Reservation.find_overlapping_with(oroom,occs).all()
                    if overlap:
                        raise ExpectedError('Overlaps with other reservations in {}.'.format(oroom.name))
                    break

    def onBookingCreated(self, sender,  **kwargs):
        room = sender.room_id
        self._checkSplitRooms(room,sender.occurrences)

    def onOccurencesChanged(self, sender,  **kwargs):
        resv  = sender.reservation
        room = resv.room_id
        self._checkSplitRooms(room, sender)
