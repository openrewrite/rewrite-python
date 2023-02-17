package org.openrewrite.python.experimental.tree.common;

import lombok.EqualsAndHashCode;
import lombok.ToString;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;

@EqualsAndHashCode
public final class ItemList<T> {

    public static <T> ItemList<T> from(T[] array) {
        return new ItemList<>(Arrays.copyOf(array, array.length));
    }

    public static <T> ItemList<T> from(Collection<T> collection) {
        Object[] array = new Object[collection.size()];
        int index = 0;
        for (T node : collection) {
            array[index++] = node;
        }
        return new ItemList<>(array);
    }

    private final Object[] items;

    private ItemList(Object[] items) {
        this.items = items;
    }

    public T get(int index) {
        //noinspection unchecked
        return (T) items[index];
    }

    public ItemList<T> withElementReplaced(int index, T newElement) {
        Object[] copy = Arrays.copyOf(this.items, this.items.length);
        copy[index] = newElement;
        return new ItemList<>(copy);
    }

    public int size() {
        return this.items.length;
    }

    public boolean isEmpty() {
        return this.size() == 0;
    }

    public ItemList<T> reversed() {
        Object[] copy = Arrays.copyOf(this.items, this.items.length);
        for (int i = 0; i < copy.length / 2; i++) {
            final int otherIndex = copy.length - i - 1;
            Object tmp = copy[i];
            copy[i] = copy[otherIndex];
            copy[otherIndex] = tmp;
        }
        return new ItemList<>(copy);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (Object item : this.items) {
            sb.append(" ").append(item).append(" ");
        }
        sb.append("]");
        return sb.toString();
    }
}
