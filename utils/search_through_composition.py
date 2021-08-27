from django.db.models import Q

def search_through_composition(query_set, search):
    filtered_query_set = query_set.filter(
                                Q(composition__name__unaccent__icontains=search) |
                                Q(composition__composers__name__unaccent__icontains=search) | 
                                #search also in the file extension, some users might look up for "wav", "flac", etc
                                Q(composition__links__midi_link__icontains=search) | 
                                Q(composition__links__flac_link__icontains=search) | 
                                Q(composition__links__pdf_link__icontains=search) | 
                                Q(composition__links__wav_link__icontains=search) 
                            ).distinct() if search else query_set 
    
    return filtered_query_set