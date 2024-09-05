import json
from django.db import models


class Finger(models.Model):
    HAND_CHOICES = [
        (0, 'Left'),
        (1, 'Right'),
    ]

    FINGER_CHOICES = [
        (0, 'Thumb'),
        (1, 'Forefinger'),
        (2, 'Middle'),
        (3, 'Ring'),
        (4, 'Little'),
    ]

    SEGMENT_CHOICES = [
        (0, 'Distal'),  # 末節
        (1, 'Middle'),  # 中截
    ]

    hand = models.PositiveSmallIntegerField(choices=HAND_CHOICES)
    finger_index = models.PositiveSmallIntegerField(choices=FINGER_CHOICES)
    segment_type = models.PositiveSmallIntegerField(choices=SEGMENT_CHOICES)

    baseline_x = models.FloatField(null=True, blank=True)
    baseline_y = models.FloatField(null=True, blank=True)
    baseline_z = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('hand', 'finger_index', 'segment_type')

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "hand": self.get_hand_display(),
            "finger_index": self.get_finger_index_display(),
            "segment_type": self.get_segment_type_display(),
        }

    @classmethod
    def initialize_fingers(cls):
        if not cls.objects.exists():
            fingers = [
                cls(hand=hand, finger_index=finger_index, segment_type=segment_type)
                for hand, _ in cls.HAND_CHOICES
                for finger_index, _ in cls.FINGER_CHOICES
                for segment_type, _ in cls.SEGMENT_CHOICES
            ]
            cls.objects.bulk_create(fingers)


class ActionLog(models.Model):
    finger = models.ForeignKey(Finger, on_delete=models.CASCADE)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return json.dumps({
            "finger": self.finger.to_dict(),
            "coordinates": {
                "x": self.x,
                "y": self.y,
                "z": self.z
            },
            "timestamp": self.timestamp.isoformat()
        })
