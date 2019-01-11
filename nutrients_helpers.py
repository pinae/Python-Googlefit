#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from datetime import datetime, timedelta


def distribute_nutrition_data_to_meals(nutrition_data, translator):
    days = split_days(nutrition_data)
    for i in range(len(days)):
        meals = cluster_meals(days[i], translator)
        days[i] = meals
    return days


def filter_data_with_calories(nutrition_data):
    filtered_data = []
    for point in nutrition_data:
        if 'calories' in point:
            filtered_data.append(point)
    return filtered_data


def split_days(nutrition_data):
    if len(nutrition_data) <= 0:
        return []
    days = []
    current_day = []
    day_end = datetime(year=nutrition_data[0]['start_time'].year, month=nutrition_data[0]['start_time'].month,
                       day=nutrition_data[0]['start_time'].day, hour=5, minute=0) + timedelta(days=1)
    for meal in nutrition_data:
        if meal['end_time'] <= day_end:
            current_day.append(meal)
        else:
            if len(current_day) > 0:
                days.append(current_day)
            current_day = []
            day_end += timedelta(days=1)
            while meal['end_time'] > day_end:
                day_end += timedelta(days=1)
            current_day.append(meal)
    if len(current_day) > 0:
        days.append(current_day)
    return days


def cluster_meals(day, translator):
    if len(day) < 1:
        return []
    sorted_points = sorted(filter_data_with_calories(day), key=lambda x: x['calories'])
    three_meal_day_clusters = [
        [{'end_time': datetime(year=day[0]['end_time'].year, month=day[0]['end_time'].month,
                               day=day[0]['end_time'].day, hour=8, minute=30), 'calories': 100, 'anchor': True}],
        [{'end_time': datetime(year=day[0]['end_time'].year, month=day[0]['end_time'].month,
                               day=day[0]['end_time'].day, hour=13, minute=30), 'calories': 100, 'anchor': True}],
        [{'end_time': datetime(year=day[0]['end_time'].year, month=day[0]['end_time'].month,
                               day=day[0]['end_time'].day, hour=19, minute=0), 'calories': 100, 'anchor': True}],
    ]
    two_meal_day_clusters = [
        [{'end_time': datetime(year=day[0]['end_time'].year, month=day[0]['end_time'].month,
                               day=day[0]['end_time'].day, hour=11, minute=0), 'calories': 150, 'anchor': True}],
        [{'end_time': datetime(year=day[0]['end_time'].year, month=day[0]['end_time'].month,
                               day=day[0]['end_time'].day, hour=20, minute=0), 'calories': 150, 'anchor': True}],
    ]
    three_meal_score = timedelta(seconds=0)
    two_meal_score = timedelta(seconds=0)
    for item in sorted_points:
        cluster_options = []
        for cluster in three_meal_day_clusters:
            cluster_time = calculate_cluster_time(cluster)
            item_score = abs(item['end_time'] - cluster_time)
            cluster_options.append((item_score, cluster))
        best_cluster_tuple = sorted(cluster_options)[0]
        best_cluster_tuple[1].append(item)
        three_meal_score += best_cluster_tuple[0]
        cluster_options = []
        for cluster in two_meal_day_clusters:
            cluster_time = calculate_cluster_time(cluster)
            item_score = abs(item['end_time'] - cluster_time)
            cluster_options.append((item_score, cluster))
        best_cluster_tuple = sorted(cluster_options)[0]
        best_cluster_tuple[1].append(item)
        two_meal_score += best_cluster_tuple[0]
    if two_meal_score / 3 * 2 <= three_meal_score:
        day_clusters = [{
            'name': translator.brunch,
            'items': two_meal_day_clusters[0]
        }, {
            'name': translator.dinner,
            'items': two_meal_day_clusters[1]
        }]
    else:
        day_clusters = [{
            'name': translator.breakfast,
            'items': three_meal_day_clusters[0]
        }, {
            'name': translator.lunch,
            'items': three_meal_day_clusters[1]
        }, {
            'name': translator.dinner,
            'items': three_meal_day_clusters[2]
        }]
    for cluster in day_clusters:
        new_item_list = []
        for item in cluster['items']:
            if 'anchor' not in item:
                new_item_list.append(item)
        cluster['items'] = new_item_list
    day_clusters = extract_snacks(day_clusters, translator)
    return day_clusters


def calculate_cluster_time(cluster):
    calories_sum = 0
    min_time = cluster[0]['end_time']
    max_time = cluster[0]['end_time']
    for item in cluster:
        if 'calories' in item:
            calories_sum += item['calories']
        else:
            calories_sum += 100
        min_time = min(min_time, item['end_time'])
        max_time = max(max_time, item['end_time'])
    mid_cluster_time = min_time + 0.5 * (max_time - min_time)
    cluster_time = mid_cluster_time
    for item in cluster:
        item_calories = item['calories'] if 'calories' in item else 100
        cluster_time += item_calories / calories_sum * (item['end_time'] - mid_cluster_time)
    return cluster_time


def extract_snacks(day_clusters, translator):
    new_clusters = []
    for i, cluster in enumerate(day_clusters):
        if len(cluster['items']) < 1:
            continue
        cluster_time = calculate_cluster_time(cluster['items'])
        sorted_items = sorted(cluster['items'], key=lambda x: x['end_time'])
        pivotal_item_no = 0
        min_time_dist = abs(sorted_items[pivotal_item_no]['end_time'] - cluster_time)
        for j, item in enumerate(sorted_items):
            time_dist = abs(item['end_time'] - cluster_time)
            if time_dist < min_time_dist:
                pivotal_item_no = j
                min_time_dist = time_dist
        if i > 0:
            snacks_at_start_no = 0
            last_time = sorted_items[pivotal_item_no]['end_time']
            for j in range(pivotal_item_no - 1, -1, -1):
                if last_time - sorted_items[j]['end_time'] > timedelta(minutes=45):
                    snacks_at_start_no = j + 1
                    break
                else:
                    last_time = sorted_items[j]['end_time']
            snacks_from_start = sorted_items[:snacks_at_start_no]
            sorted_items = sorted_items[snacks_at_start_no:]
            pivotal_item_no -= snacks_at_start_no
            if len(new_clusters) > 0 and new_clusters[-1]['name'] in [translator.morning_snack,
                                                                      translator.afternoon_snack,
                                                                      translator.bedtime_sweet,
                                                                      translator.snack]:
                new_clusters[-1]['items'] += snacks_from_start
            elif len(snacks_from_start) > 0:
                if cluster['name'] in [translator.lunch, translator.brunch]:
                    new_clusters.append({
                        'name': translator.afternoon_snack,
                        'items': snacks_from_start
                    })
                elif cluster['name'] == translator.dinner:
                    new_clusters.append({
                        'name': translator.bedtime_sweet,
                        'items': snacks_from_start
                    })
                else:
                    new_clusters.append({
                        'name': translator.snack,
                        'items': snacks_from_start
                    })
        snacks_at_end_no = len(sorted_items)
        last_time = sorted_items[pivotal_item_no]['end_time']
        for j in range(pivotal_item_no + 1, len(sorted_items)):
            if sorted_items[j]['end_time'] - last_time > timedelta(minutes=45):
                snacks_at_end_no = j
                break
            else:
                last_time = sorted_items[j]['end_time']
        snacks_from_end = sorted_items[snacks_at_end_no:]
        sorted_items = sorted_items[:snacks_at_end_no]
        new_clusters.append({
            'name': cluster['name'],
            'items': sorted_items
        })
        if len(snacks_from_end) > 0:
            if cluster['name'] == translator.breakfast:
                new_clusters.append({
                    'name': translator.morning_snack,
                    'items': snacks_from_end
                })
            elif cluster['name'] in [translator.lunch, translator.brunch]:
                new_clusters.append({
                    'name': translator.afternoon_snack,
                    'items': snacks_from_end
                })
            elif cluster['name'] == translator.dinner:
                new_clusters.append({
                    'name': translator.bedtime_sweet,
                    'items': snacks_from_end
                })
            else:
                new_clusters.append({
                    'name': translator.snack,
                    'items': snacks_from_end
                })
    return new_clusters
