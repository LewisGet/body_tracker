from django.db import models
import hashlib
import time
import json


def image_upload_rename(instance, filename):
    timestamp = int(time.time())
    md5_hash = hashlib.md5(filename.encode()).hexdigest()
    new_filename = f"{md5_hash}_{timestamp}.jpg"

    return f"upload_images/{new_filename}"


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


class HeadArmLegBody(models.Model):
    SIDE_CHOICES = [
        (0, 'Left'),
        (1, 'Right'),
    ]

    segment_names = [
        # 頭部單一點直接使用 side 0
        'Jaw',   # 下顎，不分左右，直接使用 0
        'Top',   # 頭頂，不分左右，直接使用 0
        'Nape',  # 後頸，不分左右，直接使用 0
        'Cheek', # 臉頰，臉部捕捉預留
        'Brow',  # 眉毛，臉部捕捉預留

        'Neck',     # 脖子，分左右讓肩膀好計算
        'Shoulder', # 肩膀
        'Arm',      # 手臂，後臂
        'Forearm',  # 前臂
        'Wrist',    # 手腕
        'Pelvis',   # 盆骨
        'Thigh',    # 大腿
        'Calf',     # 小腿
        'Sole',     # 腳掌
        'Chest',    # 胸
        'Back',     # 背
        'Waist',    # 腰
    ]

    SEGMENT_CHOICES = [(i, name) for i, name in enumerate(segment_names)]

    side = models.PositiveSmallIntegerField(choices=SIDE_CHOICES)
    segment_type = models.PositiveSmallIntegerField(choices=SEGMENT_CHOICES)

    baseline_x = models.FloatField(null=True, blank=True)
    baseline_y = models.FloatField(null=True, blank=True)
    baseline_z = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('side', 'segment_type')

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "side": self.get_side_display(),
            "segment_type": self.get_segment_type_display(),
        }

    @classmethod
    def initialize_parts(cls):
        if not cls.objects.exists():
            parts = [
                cls(side=side, segment_type=segment_type)
                for side, _ in cls.SIDE_CHOICES
                for segment_type, _ in cls.SEGMENT_CHOICES
            ]
            cls.objects.bulk_create(parts)


class ApiControl(models.Model):
    is_enabled = models.BooleanField(default=False)


class ActionLog(models.Model):
    finger = models.ForeignKey(Finger, on_delete=models.CASCADE, null=True, blank=True)
    head_arm_leg_body = models.ForeignKey(HeadArmLegBody, on_delete=models.CASCADE, null=True, blank=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        json_value = {
            "vector": [self.x, self.y, self.z],
            "timestamp": self.timestamp.isoformat()
        }

        if self.finger is not None:
            json_value["finger"] = self.finger.to_dict()

        if self.head_arm_leg_body is not None:
            json_value["head_arm_leg_body"] = self.head_arm_leg_body.to_dict()

        return json.dumps(json_value)


class ImageLog(models.Model):
    image = models.ImageField(upload_to=image_upload_rename)
    timestamp = models.DateTimeField()

    def __str__(self):
        return str(self.id) + " - " + str(self.timestamp)
