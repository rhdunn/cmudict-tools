;; This is a line comment.
;;@@ key1=value1 key2=value2 @@ This is a metadata comment.
;; @@ key=value @@ This is not a metadata comment.
;;@@ key3=value3 key3=value4 @@

("invalid_entry_only_word")
("invalid_entry_no_pronunciation" nil)
("invalid_entry_empty_pronunciation" nil ())
("a" nil (w aa1 n))
("b" nil (t uw1)) ; This is an entry comment.
("c" nil (th r iy1) )
("d" nil (f ao1 r)  )
("e" nil (f ay1 v))  
("f" nil (s ih1 k s)) ;@@ key1=value1 @@ metadata
("g" nil (s eh1 v ah0 n)) ; @@ key1=value1 @@ not-metadata
("goNe" nil (g ao1 n))
("UPPER" nil (uh1 p er0))
