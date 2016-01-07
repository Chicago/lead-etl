s/,/ text,/1 		# geo_id
s/,/ text,/2 		# geo_id2
s/,/ text,/3 		# geo_display_label
s/,/ decimal,/g4 	# remaining columns are decimals
s/[\.-]/_/g 		# bad column chars
s/.*/\L&/			# to lower case